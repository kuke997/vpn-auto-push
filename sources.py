import requests
from bs4 import BeautifulSoup
import re
import yaml

def fetch_from_url(name, url, protocol="clash"):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        if protocol == "clash":
            data = yaml.safe_load(res.text)
            proxies = data.get("proxies", [])
            return [{
                "region": proxy.get("country", "Unknown"),
                "city": proxy.get("server", "Unknown"),
                "protocol": proxy.get("type", "Unknown"),
                "count": 1,
                "download_url": url
            } for proxy in proxies]
        elif protocol == "txt":
            links = re.findall(r"(vmess|ss|trojan)://[a-zA-Z0-9+/=._\-]+", res.text)
            return [{
                "region": "Unknown",
                "city": "Unknown",
                "protocol": link.split("://")[0],
                "count": 1,
                "download_url": url
            } for link in links]
    except Exception as e:
        print(f"[{name}] 请求失败: {e}")
        return []

def fetch_from_html(name, url, pattern):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        matches = re.findall(pattern, res.text)
        links = list(set(matches))
        return [{
            "region": "Unknown",
            "city": "Unknown",
            "protocol": link.split("://")[0],
            "count": 1,
            "download_url": link
        } for link in links]
    except Exception as e:
        print(f"[{name}] 网页解析失败: {e}")
        return []

def fetch_all_sources():
    all_nodes = []

    sources = [
        {
            "name": "aiboboxx",
            "type": "url",
            "url": "https://raw.githubusercontent.com/aiboboxx/clashfree/main/clash.yaml",
            "protocol": "clash"
        },
        {
            "name": "freefq-txt",
            "type": "url",
            "url": "https://raw.githubusercontent.com/freefq/free/master/v2",
            "protocol": "txt"
        },
        {
            "name": "nodefree",
            "type": "html",
            "url": "https://nodefree.org/",
            "pattern": r"(https?://[^\s\"'>]+?\.(?:yaml|yml|txt))"
        },
        {
            "name": "freefq-html",
            "type": "html",
            "url": "https://freefq.com/free-ssr/",
            "pattern": r"(https?://[^\s\"'>]+?\.(?:yaml|yml|txt))"
        },
    ]

    for source in sources:
        if source["type"] == "url":
            nodes = fetch_from_url(source["name"], source["url"], source.get("protocol", "clash"))
        elif source["type"] == "html":
            nodes = fetch_from_html(source["name"], source["url"], source["pattern"])
        else:
            nodes = []
        print(f"✅ {source['name']} 获取到 {len(nodes)} 条")
        all_nodes.extend(nodes)

    return all_nodes
