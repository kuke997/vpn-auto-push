import os
import json
import requests
from bs4 import BeautifulSoup

def fetch_vpn_nodes():
    url = 'https://example.com/free-vpn-nodes'  # 替换成真实目标URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    nodes = []
    node_elements = soup.select('.vpn-node')  # 按目标网站结构改这里的选择器
    for el in node_elements:
        region = el.select_one('.region').text.strip() if el.select_one('.region') else '未知'
        city = el.select_one('.city').text.strip() if el.select_one('.city') else '未知'
        protocol = el.select_one('.protocol').text.strip() if el.select_one('.protocol') else '未知'
        count = int(el.select_one('.count').text.strip()) if el.select_one('.count') else 0
        download_url = el.select_one('a.download-link')['href'] if el.select_one('a.download-link') else ''

        node = {
            'region': region,
            'city': city,
            'protocol': protocol,
            'count': count,
            'download_url': download_url,
        }
        nodes.append(node)
    return nodes


def save_nodes_json(nodes, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    print(f"成功写入节点数据，共 {len(nodes)} 条，路径：{path}")


def main():
    nodes = fetch_vpn_nodes()
    if not nodes:
        print("未获取到任何节点，退出。")
        return

    output_path = os.path.join(os.path.dirname(__file__), 'output', 'nodes.json')
    save_nodes_json(nodes, output_path)

if __name__ == '__main__':
    main()
