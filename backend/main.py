from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .routes import encode, decode, auth, lab, doctor, admin
from .database.mongo import get_all_records
import os

app = FastAPI(title="MedHide", description="Steganography + Encryption Module")

# Ensure frontend directory exists
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')
templates = Jinja2Templates(directory=FRONTEND_DIR)

app.include_router(encode.router)
app.include_router(decode.router)
app.include_router(auth.router)
app.include_router(lab.router)
app.include_router(doctor.router)
app.include_router(admin.router)

@app.get('/health')
def health_check():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/encode", response_class=HTMLResponse)
async def read_encode(request: Request):
    return templates.TemplateResponse(request=request, name="encode.html")

@app.get("/decode", response_class=HTMLResponse)
async def read_decode(request: Request):
    return templates.TemplateResponse(request=request, name="decode.html")

@app.get('/api/records')
def api_get_records():
    return {"records": get_all_records()}

@app.get("/lab", response_class=HTMLResponse)
async def read_lab(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/doctor", response_class=HTMLResponse)
async def read_doctor(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/staff", response_class=HTMLResponse)
async def read_staff(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/admin", response_class=HTMLResponse)
async def read_admin(request: Request):
    return templates.TemplateResponse(request=request, name="admin_login.html")

@app.get("/lab/dashboard", response_class=HTMLResponse)
async def read_lab_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="lab_dashboard.html")

@app.get("/doctor/dashboard", response_class=HTMLResponse)
async def read_doctor_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="doctor_dashboard.html")

@app.get("/staff/dashboard", response_class=HTMLResponse)
async def read_staff_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="staff_dashboard.html")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def read_admin_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="admin_dashboard.html")
