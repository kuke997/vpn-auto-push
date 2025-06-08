from sources import fetch_reliable_sources
import json
import os

def main():
    print("开始爬取可靠来源的免费VPN节点...")
    nodes = fetch_reliable_sources()
    if not nodes:
        print("未获取到任何节点，退出。")
        return

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "nodes.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 nodes.json，共 {len(nodes)} 条")

if __name__ == "__main__":
    main()