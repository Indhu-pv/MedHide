from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import tempfile
import json
from ..models.patient import PatientRecord
import tempfile
from ..crypto.key_derivation import derive_key
from ..crypto.aes_gcm import encrypt
from ..crypto.hmac_envelope import wrap_payload
from ..compression.huffman import huffman_compress
from ..stego.image_scorer import score_image_bytes
from ..stego.embed import embed_bytes
from ..database.mongo import store_stego_image

router = APIRouter()

@router.post('/encode')
async def encode(
    mrd: str = Form(...),
    patient_data: str = Form(...),
    cover_image: UploadFile = File(...)
):
    key = derive_key(mrd)
    
    # Validation step: Ensure data strictly matches medical coding standard
    try:
        data_dict = json.loads(patient_data)
        validated_record = PatientRecord(**data_dict)
        # Serialize to ensure normalized structure before compression
        patient_data_str = validated_record.model_dump_json()
    except Exception as e:
        raise HTTPException(400, f"Invalid patient data format: {e}")
    
    # Step 1: Compress patient JSON
    compressed = huffman_compress(patient_data_str.encode('utf-8'))
    
    # Step 2: Encrypt
    encrypted = encrypt(compressed, key)
    
    # Step 3: Wrap in HMAC envelope
    payload = wrap_payload(encrypted, key)
    
    # Step 4: Score cover image
    img_bytes = await cover_image.read()
    if not score_image_bytes(img_bytes):
        raise HTTPException(400, 'Cover image entropy too low. Please upload an image with more variance (e.g. detailed medical scan).')
        
    # Step 5: Embed
    fd, stego_path = tempfile.mkstemp(suffix='.png', prefix=f'{mrd}_stego_')
    os.close(fd)
    
    try:
        embed_bytes(img_bytes, payload, key, stego_path)
        # Read the generated stego image
        with open(stego_path, 'rb') as f:
            stego_bytes = f.read()
    except ValueError as e:
        raise HTTPException(400, str(e))
    finally:
        if os.path.exists(stego_path):
            os.remove(stego_path)
        
    # Step 6: Store image in DB using GridFS
    store_stego_image(mrd, stego_bytes)
    
    return JSONResponse(content={"status": "success", "message": "Stego-image securely encrypted and stored in Database."})
