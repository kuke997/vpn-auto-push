import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin

HTML_SOURCES = [
    "https://freenodes.github.io/freenodes/",
    "https://freefq.com/free-ssr/",
    "https://nodefree.org/",
]

RAW_SOURCES = [
    "https://raw.githubusercontent.com/aiboboxx/clashfree/main/clash.yaml",
    "https://raw.githubusercontent.com/ermaozi01/freeclash/v2/clash.yaml",
]

def extract_links_from_html(url):
    print(f"[INFO] 解析页面: {url}")
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(href.endswith(ext) for ext in [".yaml", ".yml", ".txt"]) or "vmess://" in href:
                full = urljoin(url, href)
                links.append(full)
        return links
    except Exception as e:
        print(f"[ERROR] HTML 解析失败: {e}")
        return []

def validate_raw_link(url):
    try:
        print(f"[CHECK] 验证链接: {url}")
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        if "proxies" in res.text or "vmess://" in res.text:
            return True
    except Exception as e:
        print(f"[WARN] 验证链接失败: {e}")
    return False

def guess_region(url):
    url_lower = url.lower()
    if any(k in url_lower for k in ['sg', 'singapore']):
        return 'Asia'
    elif any(k in url_lower for k in ['jp', 'japan']):
        return 'Asia'
    elif any(k in url_lower for k in ['us', 'usa', 'america']):
        return 'North America'
    elif any(k in url_lower for k in ['de', 'fr', 'eu', 'europe']):
        return 'Europe'
    else:
        return 'Others'

def main():
    all_links = []

    # 从 HTML 页面提取链接
    for url in HTML_SOURCES:
        all_links.extend(extract_links_from_html(url))

    # 验证并添加 RAW 源
    for url in RAW_SOURCES:
        if validate_raw_link(url):
            all_links.append(url)

    all_links = list(set(all_links))  # 去重

    nodes = []
    for link in all_links:
        region = guess_region(link)
        city_match = re.search(r'//([a-zA-Z0-9\-]+)\.', link)
        city = city_match.group(1).capitalize() if city_match else 'Unknown'

        if link.endswith('.yaml') or link.endswith('.yml'):
            protocol = "Clash"
        elif 'vmess://' in link:
            protocol = "Vmess"
        else:
            protocol = "Other"

        nodes.append({
            "region": region,
            "city": city,
            "protocol": protocol,
            "count": 1,
            "download_url": link
        })

    os.makedirs("output", exist_ok=True)  # 确保 output/ 目录存在

    with open("output/nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    print(f"[DONE] 共保存 {len(nodes)} 个节点到 output/nodes.json")

if __name__ == "__main__":
    main()
