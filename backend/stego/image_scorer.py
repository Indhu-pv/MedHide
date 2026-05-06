from PIL import Image
import numpy as np
from scipy.stats import entropy
import io

def score_image_bytes(img_bytes: bytes, threshold: float = 3.0) -> bool:
    """Return True if image has sufficient entropy for steganography."""
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img_arr = np.array(img)
        scores = []
        for channel in range(3):
            hist, _ = np.histogram(img_arr[:, :, channel], bins=256, range=(0, 256))
            hist = hist / hist.sum()  # normalize
            scores.append(entropy(hist + 1e-10, base=2))
        avg_entropy = np.mean(scores)
        print(f'Image entropy: {avg_entropy:.2f} (threshold: {threshold})')
        return avg_entropy >= threshold
    except Exception as e:
        print(f"Error scoring image: {e}")
        return False
