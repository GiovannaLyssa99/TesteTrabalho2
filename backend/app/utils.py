import hashlib

def generate_hash(text: str) -> str:
    """Gera um doc_id único baseado no nome do arquivo"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
