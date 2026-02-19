import re

def apply_forward(nodes, fwds):
    """
    核心修复版：强制执行内部计数，确保编号 1, 2, 3... 递增
    """
    new_nodes = []
    
    for n in nodes:
        tag = n.get("tag", "")
        # 筛选出属于该 Tag 的所有转发规则
        matched_fwds = [f for f in fwds if f["target_tag"] == tag]
        
        if matched_fwds:
            # 关键修复：使用 enumerate 确保针对匹配的规则生成递增编号
            for i, fwd in enumerate(matched_fwds, start=1):
                n2 = n.copy()
                n2["server"] = fwd["entry_ip"]
                n2["port"] = fwd["entry_port"]
                
                # 深度清洗备注：去除旧编号和速率后缀
                raw_remark = n.get("remark", "").strip()
                # 移除末尾的空格+数字（如 " 1"）
                clean_remark = re.sub(r'\s+\d+$', '', raw_remark)
                # 移除速率后缀（如 "-5Gbps"）
                clean_remark = re.sub(r'-[\d\.]+(Gbps|Mbps|G|M)', '', clean_remark)
                
                # 重新组合备注：[名称]-[转发备注] [递增数字]
                n2["remark"] = f"{clean_remark}-{fwd['remark']} {i}"
                new_nodes.append(n2)
        else:
            # 无转发规则则保持原样
            new_nodes.append(n)
            
    return new_nodes