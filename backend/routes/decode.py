from fastapi import APIRouter, Form, HTTPException, Response
from fastapi.responses import JSONResponse
import json
from ..crypto.key_derivation import derive_key
from ..crypto.aes_gcm import decrypt
from ..crypto.hmac_envelope import unwrap_payload
from ..compression.huffman import huffman_decompress
from ..stego.extract import extract_bytes
from ..database.mongo import get_stego_image

router = APIRouter()

@router.post('/decode')
async def decode(
    mrd: str = Form(...)
):
    key = derive_key(mrd)
    
    # Step 1: Read image bytes from Database
    img_bytes = get_stego_image(mrd)
    if not img_bytes:
        raise HTTPException(404, f"No stego-image found for MRD: {mrd}")
    
    try:
        # Step 2: Extract bits
        extracted_payload = extract_bytes(img_bytes, key)
        
        # Step 3: Unwrap HMAC envelope
        encrypted = unwrap_payload(extracted_payload, key)
        
        # Step 4: Decrypt AES
        compressed = decrypt(encrypted, key)
        
        # Step 5: Decompress
        patient_data_bytes = huffman_decompress(compressed)
        
        patient_data_str = patient_data_bytes.decode('utf-8')
        return JSONResponse(content={"status": "success", "data": json.loads(patient_data_str)})
        
    except Exception as e:
        print(f"Decryption error: {e}")
        raise HTTPException(400, "Failed to decode image. Invalid image, tampered data, or incorrect MRD.")

@router.get('/image/{mrd}')
async def get_image(mrd: str):
    # Retrieve the image bytes from the Database
    img_bytes = get_stego_image(mrd)
    if not img_bytes:
        raise HTTPException(404, "Image not found")
    return Response(content=img_bytes, media_type="image/png")
