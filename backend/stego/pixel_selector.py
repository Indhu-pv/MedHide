import random
from PIL import Image

def get_pixel_indices(width: int, height: int, n_bits: int, seed_key: bytes) -> list:
    """Select n_bits pixel positions using key-seeded PRNG."""
    total_pixels = width * height
    # Seed RNG with first 8 bytes of AES key for reproducibility
    rng = random.Random(int.from_bytes(seed_key[:8], 'big'))
    
    # Randomly sample positions.
    # Note: total_pixels must be >= n_bits. We verify this before calling.
    if n_bits > total_pixels:
        raise ValueError("Not enough pixels to embed payload.")
    positions = rng.sample(range(total_pixels), n_bits)
    return positions
