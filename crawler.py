import requests
from bs4 import BeautifulSoup
import re, json, os
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
        if res.ok and ("proxies" in res.text or "vmess://" in res.text):
            return True
    except:
        pass
    return False

def guess_region(url):
    if any(k in url for k in ['sg', 'singapore']):
        return 'Asia'
    elif any(k in url for k in ['jp', 'japan']):
        return 'Asia'
    elif any(k in url for k in ['us', 'usa', 'america']):
        return 'North America'
    elif any(k in url for k in ['de', 'fr', 'eu', 'europe']):
        return 'Europe'
    else:
        return 'Others'

def main():
    all_links = []

    for url in HTML_SOURCES:
        all_links.extend(extract_links_from_html(url))

    for url in RAW_SOURCES:
        if validate_raw_link(url):
            all_links.append(url)

    all_links = list(set(all_links))  # 去重

    nodes = []
    for link in all_links:
        region = guess_region(link)
        city = re.search(r'//([a-zA-Z0-9\-]+)\.', link)
        city = city.group(1).capitalize() if city else 'Unknown'
        protocol = "Clash" if link.endswith('.yaml') else 'Vmess' if 'vmess://' in link else 'Other'

        nodes.append({
            "region": region,
            "city": city,
            "protocol": protocol,
            "count": 1,
            "download_url": link
        })

    os.makedirs("website", exist_ok=True)  # 确保 website/ 目录存在
    with open("website/nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    print(f"[DONE] 共保存 {len(nodes)} 个节点")

if __name__ == "__main__":
    main()
