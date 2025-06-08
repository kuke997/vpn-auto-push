# sources.py
import requests
from bs4 import BeautifulSoup
import yaml
import re

def get_proxypoolss():
    url = 'https://proxypoolss.pages.dev'
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        match = re.search(r'https://[^"]+\.yaml', res.text)
        if match:
            return [{'region': 'Global', 'city': '-', 'protocol': 'Clash', 'count': 1, 'download_url': match.group(0)}]
    except Exception as e:
        print(f"[proxypoolss] 请求失败: {e}")
    return []

def get_clashfree():
    url = 'https://raw.githubusercontent.com/aiboboxx/clashfree/main/clash.yml'
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return [{'region': 'GitHub', 'city': '-', 'protocol': 'Clash', 'count': 1, 'download_url': url}]
    except Exception as e:
        print(f"[clashfree] 请求失败: {e}")
    return []

def get_nodefree():
    url = 'https://nodefree.org/'
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.select('a[href$=".yaml"], a[href$=".txt"]')
        nodes = []
        for a in links:
            href = a['href']
            if not href.startswith('http'):
                href = requests.compat.urljoin(url, href)
            nodes.append({'region': 'NodeFree', 'city': '-', 'protocol': 'Clash', 'count': 1, 'download_url': href})
        return nodes
    except Exception as e:
        print(f"[nodefree] 请求失败: {e}")
    return []

def fetch_all_sources():
    return get_proxypoolss() + get_clashfree() + get_nodefree()
