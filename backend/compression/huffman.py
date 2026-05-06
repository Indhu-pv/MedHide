import zlib

def huffman_compress(data: bytes) -> bytes:
    """Compress data using zlib (which uses DEFLATE, incorporating Huffman coding)."""
    return zlib.compress(data)

def huffman_decompress(data: bytes) -> bytes:
    """Decompress data using zlib."""
    return zlib.decompress(data)
