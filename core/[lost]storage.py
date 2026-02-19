import json
import os

FILE = "data/nodes.json"

def load_nodes():
    if not os.path.exists(FILE): return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except:
        return []

def save_nodes(nodes):
    os.makedirs("data", exist_ok=True)
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=4, ensure_ascii=False)

def delete_node_by_index(index):
    nodes = load_nodes()
    if 0 <= index < len(nodes):
        removed = nodes.pop(index)
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(nodes, f, indent=4, ensure_ascii=False)
        return removed
    return None