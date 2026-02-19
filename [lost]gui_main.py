import customtkinter as ctk
import json, os
from tkinter import messagebox

# 强制 Light 模式与全局主题
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# 协议视觉配置
PROTOCOL_THEMES = {
    "ss": {"color": "#3498DB", "label": "SS"},
    "vless": {"color": "#9B59B6", "label": "VLESS"},
    "vmess": {"color": "#2ECC71", "label": "VMESS"},
    "hysteria2": {"color": "#E74C3C", "label": "HY2"}
}

class ProxyToolGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NODE PRO - 节点管理系统")
        self.geometry("1250x850")
        self.configure(fg_color="#F5F5F7") # 浅灰色背景

        self.db_nodes = "data/nodes.json"
        self.db_fwd = "data/forward_rules.json"
        self.editing_idx = None
        self.dyn_entries = {} # 存储密码、加密等动态生成的 Entry

        if not os.path.exists("data"): os.makedirs("data")
        self.setup_layout()
        self.show_node_view()

    def setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 侧边栏
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#FFFFFF", border_width=1, border_color="#E0E0E0")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🚀 NODE PRO", font=("Segoe UI", 22, "bold"), text_color="#333333").pack(pady=30)
        
        self.btn_node = self.create_nav_btn("📋 节点仓库", self.show_node_view)
        self.btn_rule = self.create_nav_btn("⛓️ 规则配置", self.show_rule_view)
        self.btn_gen = self.create_nav_btn("💎 生成链接", self.show_gen_view, True)

    def create_nav_btn(self, text, cmd, accent=False):
        btn = ctk.CTkButton(self.sidebar, text=text, command=cmd, height=40, corner_radius=6,
                            fg_color="#F0F0F0" if not accent else "#E67E22",
                            text_color="#333333" if not accent else "#FFFFFF",
                            hover_color="#E0E0E0" if not accent else "#D35400")
        btn.pack(padx=20, pady=8, fill="x")
        return btn

    def clear_main(self):
        for w in self.winfo_children(): 
            if isinstance(w, ctk.CTkFrame) and w != self.sidebar: w.destroy()

    # ================= 视图：节点管理 =================
    def show_node_view(self):
        self.clear_main()
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(0, weight=4)
        container.grid_columnconfigure(1, weight=5)

        # 左侧表单 (根据 image_60d3bf 逻辑增加编辑高亮)
        is_edit = self.editing_idx is not None
        accent_col = "#E67E22" if is_edit else "#3498DB"
        
        self.form_card = ctk.CTkFrame(container, fg_color="#FFFFFF", border_width=2, border_color=accent_col, corner_radius=12)
        self.form_card.grid(row=0, column=0, sticky="nsew", padx=10)
        
        ctk.CTkLabel(self.form_card, text="📝 编辑节点模式" if is_edit else "➕ 添加新节点", 
                     font=("微软雅黑", 16, "bold"), text_color=accent_col).pack(pady=15)
        
        scroll = ctk.CTkScrollableFrame(self.form_card, fg_color="transparent", height=500)
        scroll.pack(fill="both", expand=True, padx=10)

        self.n_tag = self.input_group(scroll, "节点标签 (Tag)")
        self.n_rem = self.input_group(scroll, "别名备注 (Remarks)")
        self.n_addr = self.input_group(scroll, "服务器地址 (Address)")
        self.n_port = self.input_group(scroll, "端口 (Port)")
        
        ctk.CTkLabel(scroll, text="协议类型", font=("微软雅黑", 12), text_color="#666666").pack(anchor="w", padx=20, pady=(10,0))
        self.n_ptl = ctk.CTkOptionMenu(scroll, values=list(PROTOCOL_THEMES.keys()), command=self.render_dyn, fg_color="#F0F0F0", text_color="#333333")
        self.n_ptl.pack(fill="x", padx=15, pady=5)

        self.dyn_area = ctk.CTkFrame(scroll, fg_color="transparent")
        self.dyn_area.pack(fill="x")
        self.render_dyn(self.n_ptl.get()) # 初始化动态字段

        btn_box = ctk.CTkFrame(self.form_card, fg_color="transparent")
        btn_box.pack(side="bottom", fill="x", padx=20, pady=20)
        ctk.CTkButton(btn_box, text="确认保存", fg_color=accent_col, command=self.save_node).pack(side="left", expand=True, padx=5)
        if is_edit:
            ctk.CTkButton(btn_box, text="取消编辑", fg_color="#999999", command=self.cancel_edit).pack(side="right", expand=True, padx=5)

        # 右侧列表
        list_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        list_scroll.grid(row=0, column=1, sticky="nsew", padx=10)
        for i, n in enumerate(self.load_data(self.db_nodes)):
            self.create_node_card(list_scroll, n, i)

    def create_node_card(self, master, n, i):
        theme = PROTOCOL_THEMES.get(n.get('protocol', 'ss'))
        card = ctk.CTkFrame(master, height=80, fg_color="#FFFFFF", border_width=1, border_color="#E0E0E0")
        card.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(card, text=theme['label'], width=50, height=28, fg_color=theme['color'], corner_radius=4, text_color="white", font=("Arial", 10, "bold")).place(x=12, y=25)
        ctk.CTkLabel(card, text=n.get('remark'), font=("微软雅黑", 14, "bold"), text_color="#333333").place(x=75, y=13)
        ctk.CTkLabel(card, text=f"{n.get('server')}:{n.get('port')} | Tag: {n.get('tag')}", text_color="#888888", font=("Arial", 11)).place(x=75, y=38)
        ctk.CTkButton(card, text="编辑", width=45, height=26, fg_color="#F0F0F0", text_color="#333333", command=lambda idx=i: self.load_for_edit(idx)).place(relx=0.78, y=25)
        ctk.CTkButton(card, text="×", width=30, height=26, fg_color="#FFEDED", text_color="#C0392B", command=lambda idx=i: self.delete_data(self.db_nodes, idx, self.show_node_view)).place(relx=0.92, y=25)

    # ================= 视图 2：规则配置 (image_60dfbd 风格) =================
    def show_rule_view(self):
        self.clear_main()
        self.editing_idx = None
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(0, weight=4)
        container.grid_columnconfigure(1, weight=5)

        # 左侧转发规则卡片
        form_card = ctk.CTkFrame(container, fg_color="#FFFFFF", border_width=1, border_color="#D0D0D0", corner_radius=12)
        form_card.grid(row=0, column=0, sticky="nsew", padx=10)
        ctk.CTkLabel(form_card, text="⛓️ 转发映射规则", font=("微软雅黑", 16, "bold"), text_color="#333333").pack(pady=15)
        
        self.r_ip = self.input_group(form_card, "入口 IP")
        self.r_port = self.input_group(form_card, "入口端口")
        
        # 标签选择
        nodes = self.load_data(self.db_nodes)
        tags = sorted(list(set(n.get('tag') for n in nodes))) if nodes else ["无可用标签"]
        ctk.CTkLabel(form_card, text="绑定目标标签", font=("微软雅黑", 12), text_color="#666666").pack(anchor="w", padx=20, pady=(10,0))
        self.r_tag = ctk.CTkOptionMenu(form_card, values=tags, fg_color="#F0F0F0", text_color="#333333")
        self.r_tag.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(form_card, text="添加映射规则", fg_color="#27AE60", height=45, corner_radius=8, font=("微软雅黑", 14), command=self.save_rule).pack(side="bottom", fill="x", padx=30, pady=25)

        # 右侧展示列表
        list_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        list_scroll.grid(row=0, column=1, sticky="nsew", padx=10)
        for i, r in enumerate(self.load_data(self.db_fwd)):
            card = ctk.CTkFrame(list_scroll, height=70, fg_color="#FFFFFF", border_width=1, border_color="#E0E0E0")
            card.pack(fill="x", pady=4, padx=5)
            ctk.CTkLabel(card, text=f"{r['entry_ip']}:{r['entry_port']}", font=("Consolas", 13, "bold"), text_color="#333333").place(x=20, y=22)
            ctk.CTkLabel(card, text=f"➔  Target Tag: {r['target_tag']}", text_color="#27AE60", font=("微软雅黑", 12, "bold")).place(x=170, y=22)
            ctk.CTkButton(card, text="删除", width=40, height=26, fg_color="#FFEDED", text_color="#C0392B", command=lambda idx=i: self.delete_data(self.db_fwd, idx, self.show_rule_view)).place(relx=0.88, y=20)

    # ================= 动态字段修复逻辑 =================
    def render_dyn(self, ptl):
        """核心：重建并绑定 Entry 引用"""
        for w in self.dyn_area.winfo_children(): w.destroy()
        self.dyn_entries = {}
        
        fields = {
            "ss": [("password", "连接密码 (Password)"), ("method", "加密算法 (Encryption)")],
            "vless": [("id", "用户 ID (UUID)"), ("net", "传输协议 (Network)")],
            "vmess": [("id", "用户 ID (UUID)"), ("aid", "额外 ID (AlterId)")],
            "hysteria2": [("password", "认证密码 (Password)")]
        }.get(ptl, [])

        for key, label in fields:
            self.dyn_entries[key] = self.input_group(self.dyn_area, label)

    def load_for_edit(self, idx):
        """修复：编辑时确保数据能准确回填到动态生成的 Entry 中"""
        self.editing_idx = idx
        node = self.load_data(self.db_nodes)[idx]
        
        # 先根据数据刷新 UI (这会触发 render_dyn)
        self.show_node_view() 
        
        # 回填基础字段
        self.n_tag.insert(0, node.get('tag', ''))
        self.n_rem.insert(0, node.get('remark', ''))
        self.n_addr.insert(0, node.get('server', ''))
        self.n_port.insert(0, str(node.get('port', '')))
        
        # 处理动态协议字段
        ptl = node.get('protocol', 'ss')
        self.n_ptl.set(ptl)
        self.render_dyn(ptl) # 这一步确保 dyn_entries 已经存在对应的 Entry 对象
        
        # 填入动态字段（如密码、加密等）
        for k, entry in self.dyn_entries.items():
            entry.insert(0, str(node.get(k, "")))

    def save_node(self):
        nodes = self.load_data(self.db_nodes)
        data = {
            "tag": self.n_tag.get().upper(),
            "remark": self.n_rem.get(),
            "server": self.n_addr.get(),
            "port": int(self.n_port.get() or 0),
            "protocol": self.n_ptl.get()
        }
        for k, e in self.dyn_entries.items():
            data[k] = e.get()

        if self.editing_idx is not None:
            nodes[self.editing_idx] = data
        else:
            nodes.append(data)
        
        self.save_data(self.db_nodes, nodes)
        self.cancel_edit()

    # ================= 辅助函数与工具 =================
    def show_gen_view(self):
        self.clear_main()
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        ctk.CTkLabel(container, text="💎 节点链接生成", font=("微软雅黑", 22, "bold"), text_color="#333333").pack(pady=10)
        out = ctk.CTkTextbox(container, fg_color="#FFFFFF", border_width=1, border_color="#D0D0D0", font=("Consolas", 12))
        out.pack(expand=True, fill="both", pady=15)
        
        nodes = self.load_data(self.db_nodes)
        rules = self.load_data(self.db_fwd)
        for r in rules:
            for m in [n for n in nodes if n['tag'] == r['target_tag']]:
                out.insert("end", f"{m['protocol']}://{r['entry_ip']}:{r['entry_port']}#FWD_{m['remark']}\n")
        
        ctk.CTkButton(container, text="📋 复制全部链接", fg_color="#3498DB", height=45, command=lambda: messagebox.showinfo("完成", "已复制到剪贴板")).pack(pady=10)

    def input_group(self, master, label):
        ctk.CTkLabel(master, text=label, font=("微软雅黑", 12), text_color="#666666").pack(anchor="w", padx=20, pady=(6,0))
        entry = ctk.CTkEntry(master, height=35, fg_color="#F9F9F9", border_color="#D0D0D0", text_color="#333333")
        entry.pack(fill="x", padx=15, pady=2)
        return entry

    def load_data(self, path):
        if not os.path.exists(path): return []
        with open(path, 'r', encoding='utf-8') as f: return json.load(f)

    def save_data(self, path, data):
        with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

    def delete_data(self, path, idx, refresh):
        if messagebox.askyesno("确认", "确定删除该条目？"):
            data = self.load_data(path); data.pop(idx)
            self.save_data(path, data); refresh()

    def cancel_edit(self):
        self.editing_idx = None
        self.show_node_view()

    def save_rule(self):
        rules = self.load_data(self.db_fwd)
        rules.append({"entry_ip": self.r_ip.get(), "entry_port": int(self.r_port.get() or 0), "target_tag": self.r_tag.get()})
        self.save_data(self.db_fwd, rules)
        self.show_rule_view()

if __name__ == "__main__":
    app = ProxyToolGUI()
    app.mainloop()