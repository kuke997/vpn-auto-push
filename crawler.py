# crawler.py
import os
import json
from sources import fetch_all_sources

def load_existing_nodes(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def deduplicate_nodes(nodes):
    seen = set()
    unique = []
    for n in nodes:
        key = (n['region'], n['city'], n['protocol'], n['download_url'])
        if key not in seen:
            seen.add(key)
            unique.append(n)
    return unique

def save_nodes_json(nodes, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 nodes.json，共 {len(nodes)} 条")

def main():
    output_path = os.path.join(os.path.dirname(__file__), 'website', 'nodes.json')
    existing = load_existing_nodes(output_path)
    new_nodes = fetch_all_sources()
    merged = new_nodes + existing  # 最新放最前
    final = deduplicate_nodes(merged)
    save_nodes_json(final, output_path)

if __name__ == '__main__':
    main()
