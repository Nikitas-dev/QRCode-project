import random
import string
import qrcode
import os
from pdf2image import convert_from_path
from pathlib import Path
from PIL import Image

# ── Token generation ──────────────────────────────────────────────────────────

def generate_tokens(amount: int = 500, length: int = 12) -> set:
    characters = string.ascii_uppercase + string.digits + string.ascii_lowercase
    existing_tokens = set()
    while len(existing_tokens) < amount:
        token = "".join(random.choices(characters, k=length))
        if token not in existing_tokens:
            existing_tokens.add(token)
    return existing_tokens

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parents[1]

TEMPLATE_PDF    = ROOT / "ticket_template.pdf"
PDF_IMAGE_DIR   = ROOT / "pdftoimages"
QR_DIR          = ROOT / "qr_codes"
OUTPUT_DIR      = ROOT / "output" / "tickets"

PDF_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
QR_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Convert PDF template → image ──────────────────────────────────────────────

images = convert_from_path(
    str(TEMPLATE_PDF),
    dpi=300,                             
    poppler_path=r"C:\poppler\bin"  
)

# Save each page; we'll use page 0 as the ticket template
for i, img in enumerate(images):
    img.save(PDF_IMAGE_DIR / f"page_{i}.png", "PNG")  # PNG keeps quality; avoid JPEG for text

TICKET_TEMPLATE = PDF_IMAGE_DIR / "page_0.png"

"""
#Open base image
base_image = Image.open() #insert the image name once ready

#Resizing the QR to fit in the ticket
qr_size = int() #insert size
qr_image = qr_image.resize((qr_size, qr_size)) #this is so that the width and the height are the same so that the qr code is a square

#Paste QR code onto image 
base_image.paste(qr_image, (base_image.width - qr_size - 10,10))

#Save result
base_image.save()
"""