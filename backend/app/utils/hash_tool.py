import hashlib
import json


def dict_hash(dictionary: dict) -> str:
    """为字典生成唯一哈希值"""
    if not dictionary:
        return ""
    # 使用sort_keys确保相同内容字典顺序不同也能生成相同哈希
    dict_str = json.dumps(dictionary, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(dict_str.encode()).hexdigest()  # 或 sha256
