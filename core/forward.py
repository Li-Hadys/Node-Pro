import re

def apply_forward(nodes, fwds):
    """
    修复版：确保编号按 [落地节点 + 转发备注] 分组重置计数
    """
    new_nodes = []
    # 用于记录每个 (落地名 + 转发备注) 组合出现的次数
    group_counter = {}
    
    for n in nodes:
        tag = n.get("tag", "")
        # 筛选出属于该 Tag 的所有转发规则
        matched_fwds = [f for f in fwds if f["target_tag"] == tag]
        
        # 备注清洗逻辑
        raw_remark = n.get("remark", "").strip()
        # 1. 移除已有的编号 (如 " 01", " 1")
        temp = re.sub(r'[\s\-_]+\d+$', '', raw_remark)
        # 2. 移除速率后缀 (如 "-1Gbps", " 5G")
        clean_landing_remark = re.sub(r'[\s\-_]*[\d\.]+\s*(Gbps|Mbps|G|M)', '', temp, flags=re.I).strip()
        
        if matched_fwds:
            for fwd in matched_fwds:
                n2 = n.copy()
                n2["server"] = fwd["entry_ip"]
                n2["port"] = fwd["entry_port"]
                
                fwd_remark = fwd.get("remark", "").strip()
                
                # 生成分组 key：由“清洗后的落地名”和“转发备注”组成
                # 这样 广电专线 和 广联专线 会分开计数
                group_key = f"{clean_landing_remark}-{fwd_remark}"
                
                # 组内计数递增
                count = group_counter.get(group_key, 0) + 1
                group_counter[group_key] = count
                
                # 重新组合备注：[落地名]-[中转名]-[原始速率] [组内编号]
                # 注意：这里我保留了原始速率后缀的展示（如果需要完全剔除，可以只用 clean_landing_remark）
                n2["remark"] = f"{clean_landing_remark}-{fwd_remark} {count}"
                
                new_nodes.append(n2)
        else:
            # 没有匹配到转发规则的节点保持原样
            new_nodes.append(n)
            
    return new_nodes
