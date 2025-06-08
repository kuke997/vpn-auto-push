# crawler.py
import os
import json
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from sources import fetch_all_sources  # 你的其他数据源函数

OUTPUT_DIR = 'output'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'nodes.json')

def fetch_freevpn_world_nodes():
    base_url = 'https://www.freevpn.world/'
    visited = set()
    nodes = []

    def is_valid_url(url):
        parsed = urlparse(url)
        return parsed.netloc.endswith('freevpn.world')

    def extract_nodes_from_text(text):
        import re
        pattern = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})')
        matches = pattern.findall(text)
        result = []
        for ip, port in matches:
            node = {
                'ip': ip,
                'port': port,
                'source': 'freevpn.world',
            }
            result.append(node)
        return result

    def crawl(url):
        if url in visited:
            return
        print(f"[freevpn.world] 爬取页面: {url}")
        visited.add(url)
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"[freevpn.world] 请求失败: {e}")
            return

        soup = BeautifulSoup(resp.text, 'html.parser')

        # 1) 提取页面内节点
        page_nodes = extract_nodes_from_text(resp.text)
        nodes.extend(page_nodes)

        # 2) 递归抓取内链
        for a in soup.find_all('a', href=True):
            href = a['href']
            abs_url = urljoin(url, href)
            if is_valid_url(abs_url) and abs_url not in visited:
                if abs_url.endswith(('.jpg','.png','.css','.js','#')):
                    continue
                time.sleep(0.5)
                crawl(abs_url)

    crawl(base_url)

    # 去重
    unique_nodes = []
    seen = set()
    for node in nodes:
        key = f"{node['ip']}:{node['port']}"
        if key not in seen:
            seen.add(key)
            unique_nodes.append(node)

    print(f"[freevpn.world] 共抓取到 {len(unique_nodes)} 条节点")
    return unique_nodes


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    all_nodes = []

    # 先获取其他源节点，fetch_all_sources()需在sources.py定义，否则删掉此行
    try:
        print("[INFO] 抓取其他数据源节点...")
        other_nodes = fetch_all_sources()
        all_nodes.extend(other_nodes)
        print(f"[INFO] 其他数据源获取到 {len(other_nodes)} 条节点")
    except Exception as e:
        print(f"[WARN] 获取其他源节点失败: {e}")

    # 抓取 freevpn.world 节点
    freevpn_nodes = fetch_freevpn_world_nodes()
    all_nodes.extend(freevpn_nodes)

    # 全节点去重
    final_nodes = []
    seen = set()
    for node in all_nodes:
        ip = node.get('ip')
        port = node.get('port')
        if not ip or not port:
            continue
        key = f"{ip}:{port}"
        if key not in seen:
            seen.add(key)
            final_nodes.append(node)

    print(f"[INFO] 去重后节点总数: {len(final_nodes)}")

    # 保存到文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_nodes, f, ensure_ascii=False, indent=2)

    print(f"[INFO] 节点已保存到 {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
