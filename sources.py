import requests
import re
import yaml
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random

# 配置设置
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": get_random_user_agent()
    })
    session.headers.update(HEADERS)
    return session

def fetch_page(url, session=None):
    """获取页面内容，带重试机制"""
    if not session:
        session = get_session()
    
    for attempt in range(3):
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            # 检查是否被重定向到验证页面
            if "just a moment" in response.text.lower() or "cloudflare" in response.text.lower():
                print(f"⚠️ 检测到Cloudflare防护，尝试绕过... (尝试 {attempt+1}/3)")
                time.sleep(2 + attempt * 2)  # 逐渐增加等待时间
                session = get_session()  # 创建新的session
                continue
                
            return response.text, session
        except Exception as e:
            print(f"请求失败 (尝试 {attempt+1}/3): {e}")
            time.sleep(1)
    
    raise Exception(f"无法获取页面: {url}")

def extract_subscription_links(html, base_url):
    """从HTML中提取订阅链接"""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    
    # 查找所有可能的链接元素
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href:
            full_url = urljoin(base_url, href)
            # 匹配常见的订阅文件扩展名
            if re.search(r'\.(yaml|yml|txt|conf|ini|v2ray|ssr?|sub|list)$', full_url, re.I):
                links.append(full_url)
    
    # 额外检查文本内容中的链接
    text_links = re.findall(r'https?://[^\s"\'<>]+?\.(yaml|yml|txt|conf|ini|v2ray|ssr?|sub|list)', html, re.I)
    for link in text_links:
        full_url = urljoin(base_url, link)
        links.append(full_url)
    
    # 去重并返回
    return list(set(links))

def parse_subscription(url, session=None):
    """解析订阅链接内容"""
    if not session:
        session = get_session()
    
    print(f"解析订阅: {url}")
    
    try:
        # 获取订阅内容
        content, _ = fetch_page(url, session)
        
        # 尝试解析为YAML
        try:
            data = yaml.safe_load(content)
            if data and isinstance(data, dict) and data.get('proxies'):
                nodes = []
                for proxy in data['proxies']:
                    nodes.append({
                        "name": proxy.get('name', 'Unknown'),
                        "type": proxy.get('type', 'Unknown'),
                        "server": proxy.get('server', 'Unknown'),
                        "port": proxy.get('port', 'Unknown'),
                        "source": url
                    })
                print(f"✅ 从YAML订阅解析出 {len(nodes)} 个节点")
                return nodes
        except yaml.YAMLError:
            pass
        
        # 尝试解析为纯文本节点列表
        nodes = []
        
        # VMess格式: vmess://...
        vmess_matches = re.findall(r'vmess://[a-zA-Z0-9+/=]+', content)
        for match in vmess_matches:
            nodes.append({
                "name": "VMess节点",
                "type": "vmess",
                "config": match,
                "source": url
            })
        
        # SS格式: ss://...
        ss_matches = re.findall(r'ss://[a-zA-Z0-9+/=]+', content)
        for match in ss_matches:
            nodes.append({
                "name": "Shadowsocks节点",
                "type": "ss",
                "config": match,
                "source": url
            })
        
        # Trojan格式: trojan://...
        trojan_matches = re.findall(r'trojan://[a-zA-Z0-9+/=]+', content)
        for match in trojan_matches:
            nodes.append({
                "name": "Trojan节点",
                "type": "trojan",
                "config": match,
                "source": url
            })
        
        # 传统IP:PORT格式
        ip_port_matches = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})', content)
        for ip, port in ip_port_matches:
            nodes.append({
                "name": f"{ip}:{port}",
                "type": "unknown",
                "server": ip,
                "port": port,
                "source": url
            })
        
        print(f"✅ 从文本订阅解析出 {len(nodes)} 个节点")
        return nodes
        
    except Exception as e:
        print(f"⚠️ 解析订阅失败: {e}")
        return []

def fetch_reliable_sources():
    """获取可靠的订阅源"""
    print("\n" + "="*50)
    print("获取可靠订阅源")
    print("="*50)
    
    session = get_session()
    all_nodes = []
    
    # 可靠的订阅源列表
    reliable_sources = [
        {
            "name": "v2raydy",
            "url": "https://raw.githubusercontent.com/v2raydy/v2ray/main/sub/vless.yml"
        },
        {
            "name": "freefq-github",
            "url": "https://raw.githubusercontent.com/freefq/free/master/v2"
        },
        {
            "name": "Pawdroid",
            "url": "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"
        },
        {
            "name": "aiboboxx",
            "url": "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2"
        },
        {
            "name": "mahdibland",
            "url": "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt"
        },
        {
            "name": "peasoft",
            "url": "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt"
        }
    ]
    
    for source in reliable_sources:
        print(f"\n处理订阅源: {source['name']} ({source['url']})")
        try:
            nodes = parse_subscription(source['url'], session)
            if nodes:
                all_nodes.extend(nodes)
                print(f"✅ 添加了 {len(nodes)} 个节点")
            else:
                print("⚠️ 未解析出节点")
        except Exception as e:
            print(f"⚠️ 处理订阅源失败: {e}")
    
    print(f"\n从可靠订阅源获取到 {len(all_nodes)} 个节点")
    return all_nodes

def save_nodes(nodes, filename="vpn_nodes.txt"):
    """保存节点到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("免费VPN节点列表\n")
        f.write("=" * 50 + "\n\n")
        
        for i, node in enumerate(nodes, 1):
            f.write(f"节点 #{i}\n")
            f.write(f"来源: {node.get('source', '未知')}\n")
            f.write(f"名称: {node.get('name', '未知')}\n")
            f.write(f"类型: {node.get('type', '未知')}\n")
            
            if 'server' in node and 'port' in node:
                f.write(f"地址: {node['server']}:{node['port']}\n")
            elif 'config' in node:
                f.write(f"配置: {node['config']}\n")
            
            f.write("-" * 50 + "\n")
    
    print(f"\n已保存 {len(nodes)} 个节点到 {filename}")

def main():
    print("开始获取免费VPN节点...")
    
    # 获取可靠源的节点
    all_nodes = fetch_reliable_sources()
    
    # 去重
    unique_nodes = []
    seen = set()
    for node in all_nodes:
        # 使用配置或服务器+端口作为唯一标识
        identifier = node.get('config', None) or f"{node.get('server', '')}:{node.get('port', '')}")
        if identifier and identifier not in seen:
            seen.add(identifier)
            unique_nodes.append(node)
    
    print("\n" + "="*50)
    print("最终结果统计")
    print("="*50)
    print(f"总节点数: {len(all_nodes)}")
    print(f"去重后节点数: {len(unique_nodes)}")
    
    # 按类型统计
    type_count = {}
    for node in unique_nodes:
        node_type = node.get('type', 'unknown')
        type_count[node_type] = type_count.get(node_type, 0) + 1
    
    print("\n节点类型分布:")
    for t, count in type_count.items():
        print(f"{t.upper()}: {count} 个")
    
    # 保存结果
    save_nodes(unique_nodes)
    
    print("\n抓取完成!")

if __name__ == "__main__":
    main()