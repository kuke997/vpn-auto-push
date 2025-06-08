import requests
import re
import yaml
from bs4 import BeautifulSoup

def fetch_from_url_list(name, url):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        links = re.findall(r'(vmess|ss|trojan)://[a-zA-Z0-9+/=._\-]+', res.text)
        return [{
            "region": "Unknown",
            "city": "Unknown",
            "protocol": link.split("://")[0],
            "count": 1,
            "download_url": url
        } for link in links]
    except Exception as e:
        print(f"[{name}] TXT链接失败: {e}")
        return []

def fetch_from_yaml_url(name, url):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = yaml.safe_load(res.text)
        proxies = data.get("proxies", [])
        return [{
            "region": proxy.get("country", "Unknown"),
            "city": proxy.get("server", "Unknown"),
            "protocol": proxy.get("type", "Unknown"),
            "count": 1,
            "download_url": url
        } for proxy in proxies]
    except Exception as e:
        print(f"[{name}] YAML解析失败: {e}")
        return []

def fetch_from_html_page(name, url, pattern):
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        matches = re.findall(pattern, res.text)
        return [{
            "region": "Unknown",
            "city": "Unknown",
            "protocol": "unknown",
            "count": 1,
            "download_url": link
        } for link in list(set(matches))]
    except Exception as e:
        print(f"[{name}] HTML页面失败: {e}")
        return []

def fetch_all_sources():
    all_nodes = []

    sources = [
        # 🔥 高可用备用 Clash 源（实测可用）
        {
            "name": "proxypoolss",
            "type": "yaml",
            "url": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/clash.yaml"
        },
        {
            "name": "pawdroid",
            "type": "yaml",
            "url": "https://raw.githubusercontent.com/pawdroid/Free-servers/main/subscriptions/clash.yaml"
        },
        {
            "name": "aiboboxx-alt",
            "type": "html",
            "url": "https://github.com/aiboboxx/clashfree",
            "pattern": r'https?://[^\s"\']+?(clash\.ya?ml|sub\.ya?ml)'
        },
        {
            "name": "freefq-html",
            "type": "html",
            "url": "https://freefq.com/free-ssr/",
            "pattern": r'https?://[^\s"\'<>]+?\.(?:yaml|yml|txt)'
        },
    ]

    for src in sources:
        if src["type"] == "yaml":
            nodes = fetch_from_yaml_url(src["name"], src["url"])
        elif src["type"] == "txt":
            nodes = fetch_from_url_list(src["name"], src["url"])
        elif src["type"] == "html":
            nodes = fetch_from_html_page(src["name"], src["url"], src["pattern"])
        else:
            nodes = []
        print(f"✅ {src['name']} 获取到 {len(nodes)} 条")
        all_nodes.extend(nodes)

    return all_nodes
