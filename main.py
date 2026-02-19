import json, os, re, urllib.parse, time
from core.parser import parse_any_link
from core.forward import apply_forward
from core.generator import encode_any_link

# 文件路径
DB_NODES = "data/nodes.json"
DB_FWD = "data/forward_rules.json"

# ANSI 颜色
C_CYAN = "\033[36m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_MAGENTA = "\033[35m"
C_BLUE = "\033[34m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

def clear_console():
    if os.name == 'nt':
        os.system('cls')
        os.system('') # 启用 Windows 颜色支持
    else:
        os.system('clear')

def load_data(file):
    if not os.path.exists(file): return []
    try:
        with open(file, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def save_data(file, data):
    with open(file, 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

def batch_add_nodes():
    print(f"\n{C_CYAN}{'='*10} 📥 批量导入原始节点 {'='*10}{C_RESET}")
    print("👉 请粘贴链接（连按两下回车开始）：")
    raw_input = ""
    while True:
        line = input()
        if not line.strip(): break
        raw_input += line + "\n"

    processed_input = re.sub(r'(ss://|vless://|hysteria2://|vmess://)', r'\n\1', raw_input)
    lines = [l.strip() for l in processed_input.split('\n') if l.strip()]

    nodes = load_data(DB_NODES)
    smart_rules = [
        {"tag": "HKL", "keywords": ["香港", "HKL"]},
        {"tag": "HKSM", "keywords": ["香港", "HKSM"]},
        {"tag": "SG-EONS", "keywords": ["新加坡", "Eons"]},
        {"tag": "JP-HY", "keywords": ["日本", "JPHyper"]},
        {"tag": "HEIWU", "keywords": ["黑五"]},
    ]

    count = 0
    for link in lines:
        try:
            link = urllib.parse.unquote(link).strip()
            node = parse_any_link(link)
            matched_tag = "未分类"
            for rule in smart_rules:
                if all(k.upper() in node['remark'].upper() for k in rule["keywords"]):
                    matched_tag = rule["tag"]
                    break
            node["tag"] = matched_tag
            nodes.append(node)
            count += 1
        except: continue
    
    save_data(DB_NODES, nodes)
    print(f"{C_GREEN}✅ 已成功导入 {count} 个节点。{C_RESET}")
    time.sleep(1)

def view_nodes():
    """图2丢失的函数已恢复"""
    nodes = load_data(DB_NODES)
    clear_console()
    print(f"{C_BOLD}{C_CYAN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}┃                    📋 原始节点仓库管理                     ┃{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}┠────────────────────────────────────────────────────────────┨{C_RESET}")

    if not nodes:
        print(f"{C_BOLD}{C_CYAN}┃{C_RESET}{' '*23}仓库目前是空的...{' '*20}{C_BOLD}{C_CYAN}┃{C_RESET}")
    else:
        for i, n in enumerate(nodes):
            tag = f"[{n.get('tag','NONE')}]"
            rem = n.get('remark','')[:35]
            print(f"{C_BOLD}{C_CYAN}┃{C_RESET}  {C_GREEN}{i:02d}{C_RESET}  {C_BOLD}{C_MAGENTA}{tag:<10}{C_RESET}  {rem:<38} {C_BOLD}{C_CYAN}┃{C_RESET}")
    
    print(f"{C_BOLD}{C_CYAN}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{C_RESET}")
    cmd = input(f"\n{C_YELLOW}输入编号删除 | 输入 'clear' 清空 | 回车返回: {C_RESET}").strip().lower()
    if cmd == 'clear':
        save_data(DB_NODES, [])
    elif cmd.isdigit() and int(cmd) < len(nodes):
        nodes.pop(int(cmd))
        save_data(DB_NODES, nodes)

def add_fwd_rule():
    nodes = load_data(DB_NODES)
    existing_tags = sorted(list(set(n.get('tag', '未分类') for n in nodes if n.get('tag'))))
    
    print(f"\n{C_BLUE}{'='*10} ⛓️ 批量录入转发规则 {'='*10}{C_RESET}")
    tag_map = {}
    if existing_tags:
        print(f"{C_BOLD}📌 可用标签 (Tag):{C_RESET}")
        for idx, tag in enumerate(existing_tags, start=1):
            tag_map[str(idx)] = tag
            print(f"  [{idx}] {tag}", end="  " if idx % 3 != 0 else "\n")
        print("\n" + "-" * 35)
    
    print("👉 粘贴 IP:端口 (例如 59.42.x.x:56953)")
    print("👉 连按两下回车结束：")
    
    input_lines = []
    while True:
        line = input().strip()
        if not line: break
        input_lines.append(line)
    
    if not input_lines: return
    
    remark = input(f"\n🏷️ 入口备注 [默认: 广电专线]: ").strip() or "广电专线"
    idx_val = input(f"🏷️ 请选择绑定的【标签序号】: ").strip()
    target_tag = tag_map.get(idx_val, "未分类").upper()

    fwds = load_data(DB_FWD)
    for entry in input_lines:
        try:
            parts = entry.split(":")
            fwds.append({
                "entry_ip": parts[0].strip(),
                "entry_port": int(parts[1].strip()),
                "remark": remark,
                "target_tag": target_tag
            })
        except: continue
        
    save_data(DB_FWD, fwds)
    print(f"{C_GREEN}✅ 规则已成功绑定至 {target_tag}。{C_RESET}")
    time.sleep(1)

def view_fwds():
    fwds = load_data(DB_FWD)
    clear_console()
    print(f"{C_BOLD}{C_BLUE}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}┃                    🛠️ 转发规则配置中心                     ┃{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}┠────────────────────────────────────────────────────────────┨{C_RESET}")
    for i, f in enumerate(fwds):
        addr = f"{f['entry_ip']}:{f['entry_port']}"
        print(f"{C_BOLD}{C_BLUE}┃{C_RESET}  {C_BLUE}{i:02d}{C_RESET}  {C_BOLD}[{f['target_tag']:<8}]{C_RESET}  {addr:<40} {C_BOLD}{C_BLUE}┃{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{C_RESET}")
    cmd = input(f"\n{C_YELLOW}输入编号删除 | 回车返回: {C_RESET}").strip()
    if cmd.isdigit() and int(cmd) < len(fwds):
        fwds.pop(int(cmd)); save_data(DB_FWD, fwds)

def gen_output():
    nodes = load_data(DB_NODES)
    fwds = load_data(DB_FWD)
    final = apply_forward(nodes, fwds)
    
    clear_console()
    print(f"{C_BOLD}{C_YELLOW}★{'━'*20}★{C_RESET}")
    print(f"{C_BOLD}{C_YELLOW}✨ 生成结果 (共 {len(final)} 个){C_RESET}")
    print(f"{C_BOLD}{C_YELLOW}★{'━'*20}★{C_RESET}\n")
    
    for n in final:
        print(encode_any_link(n))
    
    input(f"\n{C_CYAN}👉 复制完毕后，按回车返回菜单...{C_RESET}")

def menu():
    while True:
        clear_console()
        print(f"{C_CYAN}╔══════════════════════════════════════════════╗{C_RESET}")
        print(f"{C_CYAN}║{C_RESET}   {C_BOLD}{C_MAGENTA}🚀 专线节点自动化管理工具 v2.6{C_RESET}             {C_CYAN}║{C_RESET}")
        print(f"{C_CYAN}╚══════════════════════════════════════════════╝{C_RESET}")
        print(f"  {C_GREEN}[1]{C_RESET} 批量导入节点")
        print(f"  {C_GREEN}[2]{C_RESET} 查看原始仓库")
        print(f"  {C_BLUE}[3]{C_RESET} 录入转发规则")
        print(f"  {C_BLUE}[4]{C_RESET} 查看现有规则")
        print(f"  {C_YELLOW}[5]{C_BOLD} 💎 生成转发链接{C_RESET}")
        print(f"  {C_MAGENTA}[0]{C_RESET} 退出程序")
        
        choice = input(f"\n{C_CYAN}👉 请输入选项: {C_RESET}").strip()
        if choice == "1": batch_add_nodes()
        elif choice == "2": view_nodes()
        elif choice == "3": add_fwd_rule()
        elif choice == "4": view_fwds()
        elif choice == "5": gen_output()
        elif choice == "0": break

if __name__ == "__main__":
    if not os.path.exists("data"): os.makedirs("data")
    menu()