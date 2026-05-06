from PIL import Image
import numpy as np
import io
from .pixel_selector import get_pixel_indices

def embed_bytes(img_bytes: bytes, payload: bytes, key: bytes, out_path: str):
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    arr = np.array(img, dtype=np.uint8)
    
    # Store length of payload in first 32 bits (4 bytes) of the image
    # For simplicity, we embed the size in the first 32 pixels of the R channel.
    # The actual payload is embedded randomly afterwards.
    
    payload_len_bytes = len(payload).to_bytes(4, 'big')
    full_payload = payload_len_bytes + payload
    
    bits = ''.join(format(b, '08b') for b in full_payload)
    n = len(bits)
    
    flat_r = arr[:, :, 0].flatten()
    flat_g = arr[:, :, 1].flatten()
    flat_b = arr[:, :, 2].flatten()
    
    width, height = img.size
    positions = get_pixel_indices(width, height, n, key)

    for i, pos in enumerate(positions):
        channel = [flat_r, flat_g, flat_b][i % 3]
        channel[pos] = (channel[pos] & 254) | int(bits[i])

    arr[:, :, 0] = flat_r.reshape(arr.shape[:2])
    arr[:, :, 1] = flat_g.reshape(arr.shape[:2])
    arr[:, :, 2] = flat_b.reshape(arr.shape[:2])
    
    Image.fromarray(arr).save(out_path, format='PNG')
    print(f'Embedded {n} bits into {out_path}')
