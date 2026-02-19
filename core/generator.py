import urllib.parse

def encode_any_link(node):
    """将零件还原为完整的订阅链接，保留原始 query 参数"""
    protocol = node.get("protocol", "ss")
    server = node.get("server")
    port = node.get("port")
    remark = node.get("remark", "")
    
    if "full_link" in node:
        base_link = node["full_link"]
        if "@" in base_link:
            prefix, _ = base_link.rsplit("@", 1)
            query = _.split("?", 1)[1] if "?" in _ else ""
            new_main = f"{prefix}@{server}:{port}"
            if query: new_main += f"?{query}"
        else:
            new_main = f"{protocol}://{server}:{port}"
    else:
        new_main = f"{protocol}://{server}:{port}"
        
    remark_enc = urllib.parse.quote(remark)
    return f"{new_main}#{remark_enc}"