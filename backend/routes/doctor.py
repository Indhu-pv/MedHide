from fastapi import APIRouter, HTTPException, Depends
from ..database.mongo import get_all_files, create_request, get_requests_by_doctor, get_user_by_email, get_stego_image, files
from ..routes.auth import verify_token
from datetime import datetime
from ..crypto.key_derivation import derive_key
from ..crypto.aes_gcm import decrypt
from ..crypto.hmac_envelope import unwrap_payload
from ..compression.huffman import huffman_decompress
import base64

router = APIRouter()

@router.get("/api/files")
async def get_files(email: str = Depends(verify_token)):
    user = get_user_by_email(email)
    if not user or user["role"] not in ["doctor", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    files = get_all_files()
    return files

@router.post("/api/request")
async def request_file(data: dict, email: str = Depends(verify_token)):
    user = get_user_by_email(email)
    if not user or user["role"] not in ["doctor", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    file_id = data.get("file_id")
    # Find the file
    file_doc = files.find_one({"file_id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    request_data = {
        "fid": file_id,
        "fname": file_doc["file_name"],
        "owner_name": file_doc["lab_name"],
        "owner_id": file_doc["lab_id"],
        "owner_email": file_doc["lab_email"],
        "rid": user["id"],
        "rname": user["username"],
        "remail": email,
        "date": datetime.utcnow(),
        "status": "pending"
    }
    create_request(request_data)
    return {"message": "Request sent"}

@router.get("/api/requests")
async def get_requests(email: str = Depends(verify_token)):
    user = get_user_by_email(email)
    if not user or user["role"] not in ["doctor", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    requests = get_requests_by_doctor(email)
    return requests

@router.post("/api/decrypt")
async def decrypt_file(data: dict, email: str = Depends(verify_token)):
    user = get_user_by_email(email)
    if not user or user["role"] not in ["doctor", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    file_id = data.get("file_id")
    key = data.get("key")
    
    # Find the file
    file_doc = files.find_one({"file_id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if user has approved request
    from ..database.mongo import requests
    req = requests.find_one({"fid": file_id, "remail": email, "status": "approved"})
    if not req:
        raise HTTPException(status_code=403, detail="Access not approved")
    
    # Get stego image
    stego_bytes = get_stego_image(file_id)
    if not stego_bytes:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Extract payload (assuming extract function exists)
    from ..stego.extract import extract_bytes
    payload = extract_bytes(stego_bytes)
    
    # Unwrap
    decrypted = unwrap_payload(payload, derive_key(key))
    
    # Decrypt
    decompressed = decrypt(decrypted, derive_key(key))
    
    # Decompress
    message = huffman_decompress(decompressed).decode('utf-8')
    
    return {
        "fid": file_id,
        "fname": file_doc["file_name"],
        "image": f"data:image/png;base64,{base64.b64encode(stego_bytes).decode()}",
        "data": message
    }