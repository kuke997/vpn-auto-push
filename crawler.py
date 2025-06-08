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

def main():
    all_links = []

    for url in HTML_SOURCES:
        all_links.extend(extract_links_from_html(url))

    for url in RAW_SOURCES:
        if validate_raw_link(url):
            all_links.append(url)

    all_links = list(set(all_links))  # 去重
    nodes = [{"url": link} for link in all_links]

    os.makedirs("output", exist_ok=True)
    with open("output/nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

    print(f"[DONE] 共保存 {len(nodes)} 个节点链接")

if __name__ == "__main__":
    main()
