from PIL import Image
import numpy as np
import io
from .pixel_selector import get_pixel_indices

def extract_bytes(img_bytes: bytes, key: bytes) -> bytes:
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    arr = np.array(img, dtype=np.uint8)
    
    flat_r = arr[:, :, 0].flatten()
    flat_g = arr[:, :, 1].flatten()
    flat_b = arr[:, :, 2].flatten()
    
    width, height = img.size
    
    # First, we need to extract the length. 
    # Since we mixed length + payload, we don't know the size yet.
    # A standard way is to extract the first 32 bits to get the length.
    # So we get positions for 32 bits first.
    pos_32 = get_pixel_indices(width, height, 32, key)
    
    len_bits = []
    for i, pos in enumerate(pos_32):
        channel = [flat_r, flat_g, flat_b][i % 3]
        len_bits.append(str(channel[pos] & 1))
        
    len_str = ''.join(len_bits)
    payload_len = int(len_str, 2)
    
    # Now we know the total number of bits = (4 + payload_len) * 8
    total_bits = (4 + payload_len) * 8
    
    if total_bits > width * height:
        raise ValueError("Invalid length extracted, perhaps wrong key or tampered image.")
        
    positions = get_pixel_indices(width, height, total_bits, key)
    
    extracted_bits = []
    # Skip the first 32 bits which are the length
    for i in range(32, total_bits):
        pos = positions[i]
        channel = [flat_r, flat_g, flat_b][i % 3]
        extracted_bits.append(str(channel[pos] & 1))
        
    # Convert bits to bytes
    extracted_bytes = bytearray()
    for i in range(0, len(extracted_bits), 8):
        byte_str = ''.join(extracted_bits[i:i+8])
        extracted_bytes.append(int(byte_str, 2))
        
    return bytes(extracted_bytes)
