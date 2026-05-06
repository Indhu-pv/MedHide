import smtplib
from email.message import EmailMessage

from fastapi import APIRouter, HTTPException
from ..database.mongo import get_all_users, get_all_requests, update_request_status, files

router = APIRouter()

@router.get("/api/admin/employees")
async def get_employees():
    users = get_all_users()
    return users

@router.get("/api/admin/requests")
async def get_requests():
    requests = get_all_requests()
    return requests

@router.post("/api/admin/send-key")
async def send_key(data: dict):
    fid = data.get("fid")
    rid = data.get("rid")
    # Find the file and get the key
    file_doc = files.find_one({"file_id": fid})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    key = file_doc.get("key")
    # In a real app, send email with key
    # For now, just update status
    update_request_status(fid, rid, "approved")
    return {"message": f"Key sent: {key}"}