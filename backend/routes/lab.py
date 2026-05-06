from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from ..models.file import LabFile
from ..database.mongo import create_file, get_user_by_email
from ..routes.auth import verify_token
from datetime import datetime
import os
from PIL import Image
import io
import tempfile
from ..crypto.key_derivation import derive_key
from ..crypto.aes_gcm import encrypt
from ..crypto.hmac_envelope import wrap_payload
from ..compression.huffman import huffman_compress
from ..stego.image_scorer import score_image_bytes
from ..stego.embed import embed_bytes
from ..database.mongo import store_stego_image

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/api/lab/upload")
async def upload_file(
    file_id: str = Form(...),
    file_name: str = Form(...),
    message: str = Form(...),
    key: str = Form(...),
    file: UploadFile = File(...),
    email: str = Depends(verify_token)
):
    user = get_user_by_email(email)
    if not user or user["role"] != "lab":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Use the key for encryption
    encryption_key = derive_key(key)
    
    # Compress message
    compressed = huffman_compress(message.encode('utf-8'))
    
    # Encrypt
    encrypted = encrypt(compressed, encryption_key)
    
    # Wrap in HMAC envelope
    payload = wrap_payload(encrypted, encryption_key)
    
    # Read cover image
    img_bytes = await file.read()
    if not score_image_bytes(img_bytes):
        raise HTTPException(400, 'Cover image entropy too low. Please upload an image with more variance.')
        
    # Embed
    fd, stego_path = tempfile.mkstemp(suffix='.png', prefix=f'{file_id}_stego_')
    os.close(fd)
    embed_bytes(img_bytes, payload, encryption_key, stego_path)
    
    # Store in GridFS
    with open(stego_path, 'rb') as f:
        stego_bytes = f.read()
    store_stego_image(file_id, stego_bytes)
    
    # Clean up
    os.unlink(stego_path)

    # Save file metadata
    file_data = {
        "file_id": file_id,
        "file_name": file_name,
        "lab_id": user["id"],
        "lab_name": user["username"],
        "lab_email": email,
        "role": user["role"],
        "date": datetime.utcnow(),
        "status": "uploaded",
        "key": key,
        "image_path": f"{file_id}_stego.png"  # GridFS filename
    }
    create_file(file_data)
    return {"message": "File uploaded and data embedded successfully"}