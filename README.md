# 🛡️ MedHide

**Steganography + Encryption Module — Software Prototype**

> **Security Through Invisibility:** A secure medical data storage and transfer system combining AES-256 encryption with advanced LSB steganography to make patient records invisible to unauthorized parties.

---

## 👥 Team & Project Info
- **Team Name:** MedHide
- **Institute:** Velammal Engineering College, Chennai
- **Theme:** Health & Inclusivity
- **Domain:** Secure Medical Data Storage & Transfer
- **Hackathon:** CMRIT Hackathon, Bengaluru
- **Team Leader:** Geethanjali V N
- **Members:** Indhu P, Nikhil S, James Jacob I

## Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI + Uvicorn** (web framework + ASGI server)

### Security & Encryption
- **cryptography** — AES-256-GCM + PBKDF2-HMAC-SHA256 key derivation
- **stegano** — LSB steganography base library

### Image Processing
- **Pillow** — image read/write/manipulation
- **numpy + scipy** — pixel array operations + entropy calculation for cover image scoring

### Data & Compression
- **pydantic** — patient data validation models
- **python-multipart** — file upload handling (cover images via FastAPI)
- **Huffman compression** — implemented manually in `compression/huffman.py` (no separate library needed)

### Database
- **pymongo** — MongoDB driver (local instance or Atlas)

### IoT / Hardware (stub only for now)
- **pyserial** — Arduino serial communication placeholder in `rfid_stub/rfid_mock.py`

### Testing
- **pytest**

### Storage
- Local filesystem or AWS S3 (S3 integration deferred — boto3 added when needed)

### Frontend
- Plain HTML + CSS + JavaScript (no framework needed for prototype)
- Jinja2 templating via FastAPI's built-in support

*Note: This repository covers the complete software prototype. The RFID/IoT hardware integration (Arduino + RFID RC522) is documented separately and will be implemented later.*

---

## 🎯 The Problem We Solve
Medical data breaches are increasing globally. Even when data is encrypted, the mere presence of encrypted blobs signals to attackers that sensitive data exists — making those systems high-value targets. In low-resource and rural hospitals, secure infrastructure is often unavailable, and patient records are exposed.

### 💡 Core Innovation: Security Through Invisibility
- **Encryption alone** protects the content but exposes the existence of the data.
- **Steganography** hides the data inside a cover image — attackers see only a normal medical photo.
- **MedHide combines both:** Encrypt first, then hide inside the image. Double-layer protection.

---

## 🏗️ Creative & Productive Security Architecture

### 1. Layered Encryption Pipeline
Rather than raw AES, MedHide implements a three-layer encryption pipeline:
- **Layer 1 — AES-256-GCM (Authenticated Encryption):** Encrypts the patient JSON record. GCM mode provides both confidentiality AND integrity (tamper detection). Key derived using PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP 2024 recommendation).
- **Layer 2 — Huffman Compression before Encryption:** Patient records (JSON) are Huffman-compressed BEFORE encryption. Smaller payload = more images can carry records + less stego distortion.
- **Layer 3 — Payload Envelope with HMAC:** Final payload = `version_byte` + `HMAC-SHA256(ciphertext)` + `ciphertext`. Detects corruption or tampering before decryption.

### 2. Advanced Steganography: Beyond Basic LSB
Basic LSB is easy to detect. MedHide uses a smarter approach:
- **Adaptive Randomized LSB:** Pixels are selected using a PRNG seeded from the AES key. The same key required to decrypt is also required to LOCATE the data in the image.
- **Multi-channel Dual-bit Embedding:** Embed 2 bits per channel (R, G, B) instead of 1 — but only in high-variance regions (texture/edges).
- **Cover Image Selection Score:** Images are scored using entropy analysis. Low-entropy images are rejected to avoid visual artifacts.

### 3. DICOM-as-Cover-Image
Instead of arbitrary images, MedHide uses the patient's own DICOM medical scans (X-ray, MRI thumbnails) as the cover image.
- Natural plausible deniability.
- The cover image itself carries meaningful clinical context.
- Stego image is still a valid DICOM PNG.

### 4. Unique Key Derivation per Patient
Each patient's encryption key is derived from:  
`Patient MRD number` + `Hospital salt (server-side)` + `RFID card UID (hardware, deferred)`.

---

## 📁 Project Structure

```text
medhide/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── crypto/
│   │   ├── aes_gcm.py           # AES-256-GCM encrypt/decrypt
│   │   ├── key_derivation.py    # PBKDF2 key from patient MRD
│   │   └── hmac_envelope.py     # Payload envelope + HMAC check
│   ├── stego/
│   │   ├── embed.py             # Adaptive randomized LSB embed
│   │   ├── extract.py           # LSB extract + verify
│   │   ├── image_scorer.py      # Entropy-based cover image scorer
│   │   └── pixel_selector.py    # PRNG pixel selection from key
│   ├── compression/
│   │   └── huffman.py           # Huffman compress/decompress
│   ├── models/
│   │   └── patient.py           # Patient data Pydantic model
│   ├── routes/
│   │   ├── encode.py            # POST /encode endpoint
│   │   └── decode.py            # POST /decode endpoint
│   └── database/
│   │   └── mongo.py             # MongoDB connection + queries
├── frontend/
│   ├── index.html
│   ├── encode.html
│   └── decode.html
├── rfid_stub/                   # Placeholder for RFID integration (Hardware deferred)
│   └── rfid_mock.py             # Mock RFID UID for testing without hardware
├── tests/
│   ├── test_crypto.py
│   ├── test_stego.py
│   └── test_api.py
├── requirements.txt
└── README.md                    # This file
```

---

## ⚙️ Environment Setup

### Prerequisites
- **Python:** 3.10 or higher
- **MongoDB:** Local instance or MongoDB Atlas
- **OS:** Linux / macOS / Windows (WSL recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-team/medhide.git
cd medhide

# Create virtual environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 FastAPI Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/encode` | Accept patient JSON + cover image → return stego image |
| `POST` | `/decode` | Accept stego image + MRD number → return patient data |
| `GET` | `/score-image` | Return entropy score of an uploaded image |
| `POST` | `/register` | Register patient MRD and map to stego image in DB |
| `GET` | `/health` | Health check endpoint |

---

## 🧪 Testing the Prototype

```bash
# Run all tests
pytest tests/ -v

# Test encryption round-trip
python -m pytest tests/test_crypto.py -v

# Test steganography (requires a sample image)
python -m pytest tests/test_stego.py -v

# Start the API server
uvicorn backend.main:app --reload --port 8000

# Test encode via curl
curl -X POST http://localhost:8000/encode \
  -F 'mrd=MRD001' \
  -F 'patient_data={"name":"Test Patient","diagnosis":"Hypertension"}' \
  -F 'cover_image=@sample_xray.png' \
  --output stego_output.png
```

---

## 🔌 RFID Integration (Hardware - Deferred to Later Phase)

The hardware RFID module is intentionally left as a stub in this software prototype. 

*We still have to implement the hardware part later on.* When ready, the mock UID reading will be replaced with an actual serial read from the Arduino RC522 setup. The patient key derivation is already designed to accept the UID to bind the encryption key to the physical card.

**What is left for the Hardware Implementation:**
- Arduino UNO + RFID RC522 wiring and firmware.
- Serial communication from Arduino to Python backend.
- UID-based key binding: `derive_key(mrd, uid=rfid_uid)`.
- Physical patient card provisioning workflow.
- Anti-relay and anti-clone protections (Challenge-Response and Cryptographic Key Splitting).
