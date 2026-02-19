import urllib.parse

def parse_any_link(link):
    """解析 ss/vless/hysteria2 链接，保留核心参数和备注"""
    link = urllib.parse.unquote(link)
    original_link = link.strip()
    remark = ""
    if "#" in link:
        link_no_remark, remark = original_link.split("#", 1)
        remark = urllib.parse.unquote(remark)
    else:
        link_no_remark = original_link

    if "://" not in link_no_remark:
        raise ValueError("无效的链接格式")
    
    protocol = link_no_remark.split("://")[0]
    
    try:
        main_part = link_no_remark.split("://")[1]
        # 寻找最后一个 @，避免用户名里包含 @ 导致解析错误
        server_info = main_part.split("@")[-1]
        # 移除查询参数部分提取 host:port
        server_host_port = server_info.split("?")[0]
        
        if ":" in server_host_port:
            server = server_host_port.split(":")[0]
            port = int(server_host_port.split(":")[1])
        else:
            server = server_host_port
            port = 443 
    except Exception as e:
        raise ValueError(f"地址解析失败: {e}")

    return {
        "protocol": protocol,
        "server": server,
        "port": port,
        "remark": remark,
        "full_link": link_no_remark, # 存储不带备注的原始骨架
        "tag": "" 
    }