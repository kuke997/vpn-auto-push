import requests
from bs4 import BeautifulSoup
import re
import yaml

def fetch_from_yaml(name, url):
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
        print(f"[{name}] YAML 源失败: {e}")
        return []

def fetch_from_txt(name, url):
    try:
        res = requests.get(url, timeout=10)
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
        print(f"[{name}] TXT 源失败: {e}")
        return []

def fetch_from_html_links(name, url, pattern):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        matches = re.findall(pattern, res.text)
        links = list(set(matches))
        return [{
            "region": "Unknown",
            "city": "Unknown",
            "protocol": link.split("://")[0],
            "count": 1,
            "download_url": link
        } for link in links if link.startswith("http")]
    except Exception as e:
        print(f"[{name}] HTML 解析失败: {e}")
        return []

def fetch_all_sources():
    all_nodes = []

    sources = [
        # 高可用 GitHub 源
        {
            "name": "freenodes-clash",
            "type": "yaml",
            "url": "https://raw.githubusercontent.com/freenodes/freenodes/main/clash.yaml"
        },
        {
            "name": "nodefree-sub",
            "type": "txt",
            "url": "https://raw.githubusercontent.com/kxswa/free-v2ray-subscribe/main/sub/subscribe.txt"
        },
        {
            "name": "v2cross-sub",
            "type": "txt",
            "url": "https://raw.githubusercontent.com/vpei/Free-Node-Merge/main/o.yaml"
        },
        {
            "name": "freefq-html",
            "type": "html",
            "url": "https://freefq.com/free-ssr/",
            "pattern": r'https?://[^\s"\'<>]+?\.(?:yaml|yml|txt)'
        },
        {
            "name": "nodefree-html",
            "type": "html",
            "url": "https://nodefree.org/",
            "pattern": r'https?://[^\s"\'<>]+?\.(?:yaml|yml|txt)'
        },
    ]

    for src in sources:
        if src["type"] == "yaml":
            nodes = fetch_from_yaml(src["name"], src["url"])
        elif src["type"] == "txt":
            nodes = fetch_from_txt(src["name"], src["url"])
        elif src["type"] == "html":
            nodes = fetch_from_html_links(src["name"], src["url"], src["pattern"])
        else:
            nodes = []
        print(f"✅ {src['name']} 获取到 {len(nodes)} 条")
        all_nodes.extend(nodes)

    return all_nodes
