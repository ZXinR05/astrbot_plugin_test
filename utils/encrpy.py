import hashlib


def md5(str_input: str) -> str:
    """计算字符串的 MD5 值"""
    md5_hash = hashlib.md5()
    md5_hash.update(str_input.encode("utf-8"))
    return md5_hash.hexdigest()