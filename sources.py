import requests
import re
import yaml
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 设置通用请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

def fetch_from_url_list(name, url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        links = re.findall(r'(vmess|ss|trojan)://[a-zA-Z0-9+/=._\-]+', res.text)
        return [{
            "region": "Unknown",
            "city": "Unknown",
            "protocol": link.split("://")[0],
            "count": 1,
            "download_url": url,
            "source": name
        } for link in links]
    except Exception as e:
        print(f"[{name}] TXT链接失败: {e}")
        return []

def fetch_from_yaml_url(name, url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = yaml.safe_load(res.text)
        proxies = data.get("proxies", [])
        return [{
            "region": proxy.get("country", "Unknown"),
            "city": proxy.get("server", "Unknown"),
            "protocol": proxy.get("type", "Unknown"),
            "count": 1,
            "download_url": url,
            "source": name
        } for proxy in proxies]
    except Exception as e:
        print(f"[{name}] YAML解析失败: {e}")
        return []

def fetch_from_html_page(name, url, pattern):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        matches = re.findall(pattern, res.text)
        # 转换为绝对URL
        absolute_matches = [urljoin(url, m) for m in matches]
        return list(set(absolute_matches))  # 返回去重后的绝对URL列表
    except Exception as e:
        print(f"[{name}] HTML页面失败: {e}")
        return []

def parse_subscription_links(name, url):
    """根据订阅链接类型调用对应的解析函数"""
    if url.endswith(('.yaml', '.yml')):
        return fetch_from_yaml_url(name, url)
    elif url.endswith('.txt'):
        return fetch_from_url_list(name, url)
    return []

def fetch_freevpn_world():
    print("[freevpn.world] 开始爬取")
    base_url = "https://www.freevpn.world/"
    visited = set()
    nodes = []

    def crawl(url):
        if url in visited:
            return
        visited.add(url)
        print(f"[freevpn.world] 请求 URL: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"[freevpn.world] 请求失败: {e}")
            return

        soup = BeautifulSoup(resp.text, "html.parser")

        # 网页文本中匹配IP:PORT格式，简易提取节点
        text = soup.get_text()
        pattern = re.compile(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)[:：](\d{2,5})')
        found = 0
        for match in pattern.finditer(text):
            ip, port = match.groups()
            node = {
                "region": "Unknown",
                "city": "Unknown",
                "protocol": "unknown",
                "count": 1,
                "download_url": f"{ip}:{port}",
                "source": "freevpn.world"
            }
            nodes.append(node)
            found += 1
        print(f"[freevpn.world] 页面发现节点数: {found}")

        # 递归爬取同域名其他页面链接
        links = soup.find_all("a", href=True)
        for a in links:
            href = a["href"]
            full_url = urljoin(url, href)
            if full_url.startswith(base_url) and full_url not in visited:
                crawl(full_url)

    crawl(base_url)
    print(f"[freevpn.world] 爬取结束，节点总数: {len(nodes)}")

    # 去重
    unique_nodes = {}
    for n in nodes:
        key = n["download_url"]
        unique_nodes[key] = n
    return list(unique_nodes.values())

def fetch_all_sources():
    all_nodes = []

    # 更新资源列表 - 替换失效的链接
    sources = [
        # 有效的YAML资源
        {
            "name": "v2raydy",
            "type": "yaml",
            "url": "https://raw.githubusercontent.com/v2raydy/v2ray/main/sub/vless.yml"
        },
        {
            "name": "freefq",
            "type": "yaml",
            "url": "https://raw.githubusercontent.com/freefq/free/master/v2"
        },
        # HTML资源
        {
            "name": "freefq-html",
            "type": "html",
            "url": "https://freefq.com/free-ssr/",
            "pattern": r'(?:href|src)=["\'](https?://[^\s"\'<>]+?\.(?:yaml|yml|txt|conf|ini))'
        },
        {
            "name": "github-aiboboxx",
            "type": "html",
            "url": "https://github.com/aiboboxx/clashfree",
            "pattern": r'(?:href|src)=["\'](https?://[^\s"\'<>]+?\.(?:yaml|yml|txt|conf|ini))'
        }
    ]

    for src in sources:
        nodes = []
        if src["type"] == "yaml":
            nodes = fetch_from_yaml_url(src["name"], src["url"])
        elif src["type"] == "txt":
            nodes = fetch_from_url_list(src["name"], src["url"])
        elif src["type"] == "html":
            # 获取页面中的订阅链接
            subscription_links = fetch_from_html_page(src["name"], src["url"], src["pattern"])
            print(f"[{src['name']}] 发现 {len(subscription_links)} 个订阅链接")
            
            # 对每个订阅链接进行二次解析
            for i, link in enumerate(subscription_links):
                print(f"[{src['name']}] 解析订阅链接 {i+1}/{len(subscription_links)}: {link}")
                sub_name = f"{src['name']}-sub-{i}"
                nodes += parse_subscription_links(sub_name, link)
        
        print(f"✅ {src['name']} 获取到 {len(nodes)} 条节点")
        all_nodes.extend(nodes)

    # 调用 freevpn.world 爬取
    print("开始爬取 freevpn.world 节点...")
    freevpn_nodes = fetch_freevpn_world()
    print(f"freevpn.world 抓取到节点数: {len(freevpn_nodes)}")
    all_nodes.extend(freevpn_nodes)

    return all_nodes

def save_to_file(nodes, filename="nodes.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for node in nodes:
            f.write(f"来源: {node['source']}\n")
            f.write(f"协议: {node['protocol']}\n")
            f.write(f"地区: {node['region']} - {node['city']}\n")
            f.write(f"地址: {node['download_url']}\n")
            f.write("-" * 50 + "\n")
    print(f"已保存 {len(nodes)} 个节点到 {filename}")

# 测试代码
if __name__ == "__main__":
    print("开始抓取所有资源...")
    all_nodes = fetch_all_sources()
    
    if not all_nodes:
        print("未获取到任何节点，退出。")
        exit(1)
    
    print("\n最终结果统计:")
    print(f"总节点数: {len(all_nodes)}")
    
    # 按来源统计
    source_count = {}
    for node in all_nodes:
        source = node.get("source", "unknown")
        source_count[source] = source_count.get(source, 0) + 1
    
    print("\n来源分布:")
    for source, count in source_count.items():
        print(f"{source}: {count} 个节点")
    
    # 保存结果到文件
    save_to_file(all_nodes)
