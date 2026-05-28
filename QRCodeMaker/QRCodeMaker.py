import random
import string
import qrcode
from pdf2image import convert_from_path
from pathlib import Path
from PIL import Image
import os

# ── Token generation ──────────────────────────────────────────────────────────

def generate_tokens(amount: int = 500, length: int = 12) -> set:
    characters = string.ascii_uppercase + string.digits + string.ascii_lowercase
    existing_tokens = set()

    while len(existing_tokens) < amount:
        token = "".join(random.choices(characters, k=length))
        existing_tokens.add(token)

    return existing_tokens

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

TEMPLATE_PDF = ROOT / "ticket_template.pdf"

PDF_IMAGE_DIR = ROOT / "pdftoimages"
QR_DIR = ROOT / "qr_codes"
OUTPUT_DIR = ROOT / "output" / "tickets"
PDF_PAGE_OUTPUT = ROOT / "output" / "tickets_to_print.pdf"

PDF_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
QR_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Poppler path ──────────────────────────────────────────────────────────────
# IMPORTANT:
# This folder must contain pdfinfo.exe and pdftoppm.exe

POPPLER_PATH = Path(r"D:\poppler-26.02.0\Library\bin")

if not (POPPLER_PATH / "pdfinfo.exe").exists():
    raise FileNotFoundError(
        f"Poppler was not found at:\n{POPPLER_PATH}\n\n"
        "Make sure this folder contains pdfinfo.exe and pdftoppm.exe."
    )

# ── Check PDF exists ──────────────────────────────────────────────────────────

if not TEMPLATE_PDF.exists():
    raise FileNotFoundError(
        f"Could not find ticket_template.pdf at:\n{TEMPLATE_PDF}\n\n"
        "Put ticket_template.pdf in the same folder as this Python file."
    )

# ── Convert PDF template → image ──────────────────────────────────────────────

images = convert_from_path(
    str(TEMPLATE_PDF),
    dpi=300,
    poppler_path=str(POPPLER_PATH)
)

for i, img in enumerate(images):
    img.save(PDF_IMAGE_DIR / f"page_{i}.png", "PNG") 

TICKET_TEMPLATE = PDF_IMAGE_DIR / "page_0.png"

print("PDF converted to PNG successfully!")
print(f"Saved images in: {PDF_IMAGE_DIR}")
print(f"Ticket template image: {TICKET_TEMPLATE}")

# ── Placing QR Codes on tickets ──────────────────────────────────────────────

# List of QRs
qr_list = list(QR_DIR.glob("*.png"))

for qr_path in qr_list:
    ticket = Image.open(TICKET_TEMPLATE)
    qr = Image.open(qr_path)
    qr = qr.resize((350, 350), Image.LANCZOS)
    
    qr_w, qr_h = qr.size
    ticket_w, ticket_h = ticket.size
    center_x = int(ticket_w * 0.65)
    center_y = int(ticket_h * 0.6)
    x = center_x - (qr_w // 2)
    y = center_y - (qr_h // 2)

    ticket.paste(qr, (x, y))
    ticket.save(OUTPUT_DIR / f"Ticket{qr_path.stem}.png")

# ── Placing Tickets on A4 PDF for printing ──────────────────────────────────────────────

A4_w , A4_h = 2480, 3508
pages = []
ticket_list = list(OUTPUT_DIR.glob("*.png"))

for i in range(0, len(ticket_list), 4):
    group = ticket_list[i:i+4]
    page = Image.new("RGB", (A4_w, A4_h), (255, 255, 255))
    space_per_ticket = A4_h // 4
    
    for j, ticket_path in enumerate(group):
        ticket = Image.open(ticket_path).convert("RGB")
        ticket = ticket.resize((A4_w, space_per_ticket), Image.LANCZOS)
        y = j * space_per_ticket
        page.paste(ticket, (0,y))

    pages.append(page)

pages[0].save(PDF_PAGE_OUTPUT, save_all=True, append_images=pages[1:], resolution=300)