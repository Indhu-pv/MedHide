import os
from pymongo import MongoClient
import gridfs
from datetime import datetime
import bcrypt

# Use local memory db or something simple for prototype if MONGO_URI is missing.
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.medhide
fs = gridfs.GridFS(db)

# User collection
users = db.users

# Files collection
files = db.files

# Requests collection
requests = db.requests

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(user_data: dict):
    user_data['password_hash'] = hash_password(user_data.pop('password'))
    user_data['created_at'] = datetime.utcnow()
    return users.insert_one(user_data).inserted_id

def get_user_by_email(email: str):
    return users.find_one({"email": email})

def get_user_by_id(user_id: str):
    return users.find_one({"id": user_id})

def get_all_users():
    return list(users.find())

def create_file(file_data: dict):
    return files.insert_one(file_data).inserted_id

def get_all_files():
    return list(files.find())

def get_files_by_lab(lab_email: str):
    return list(files.find({"lab_email": lab_email}))

def update_file_status(file_id: str, status: str):
    files.update_one({"file_id": file_id}, {"$set": {"status": status}})

def create_request(request_data: dict):
    return requests.insert_one(request_data).inserted_id

def get_all_requests():
    return list(requests.find())

def get_requests_by_doctor(doctor_email: str):
    return list(requests.find({"remail": doctor_email}))

def update_request_status(fid: str, rid: str, status: str):
    requests.update_one({"fid": fid, "rid": rid}, {"$set": {"status": status}})

def store_stego_image(mrd: str, image_bytes: bytes):
    # Check if already exists for this MRD and delete old version
    existing = fs.find_one({"filename": f"{mrd}_stego.png"})
    if existing:
        fs.delete(existing._id)
    # Store new image using GridFS
    fs.put(image_bytes, filename=f"{mrd}_stego.png")

def get_stego_image(mrd: str) -> bytes:
    # Retrieve the image by MRD filename
    file = fs.find_one({"filename": f"{mrd}_stego.png"})
    if file:
        return file.read()
    return None

def get_all_records():
    """Returns a list of metadata for all stored stego-images."""
    records = []
    # GridFS stores file metadata in the fs.files collection
    for f in db.fs.files.find().sort("uploadDate", -1):
        filename = f.get("filename", "")
        if filename.endswith("_stego.png"):
            mrd = filename.replace("_stego.png", "")
            records.append({
                "mrd": mrd,
                "upload_date": f.get("uploadDate").isoformat() if f.get("uploadDate") else "Unknown",
                "size_bytes": f.get("length", 0)
            })
    return records

def store_stego_image(mrd: str, image_bytes: bytes):
    # Check if already exists for this MRD and delete old version
    existing = fs.find_one({"filename": f"{mrd}_stego.png"})
    if existing:
        fs.delete(existing._id)
    # Store new image using GridFS
    fs.put(image_bytes, filename=f"{mrd}_stego.png")

def get_stego_image(mrd: str) -> bytes:
    # Retrieve the image by MRD filename
    file = fs.find_one({"filename": f"{mrd}_stego.png"})
    if file:
        return file.read()
    return None

def get_all_records():
    """Returns a list of metadata for all stored stego-images."""
    records = []
    # GridFS stores file metadata in the fs.files collection
    for f in db.fs.files.find().sort("uploadDate", -1):
        filename = f.get("filename", "")
        if filename.endswith("_stego.png"):
            mrd = filename.replace("_stego.png", "")
            records.append({
                "mrd": mrd,
                "upload_date": f.get("uploadDate").isoformat() if f.get("uploadDate") else "Unknown",
                "size_bytes": f.get("length", 0)
            })
    return records
