import fitz  # PyMuPDF

def pdf_to_png(pdf_path: str, png_path: str, dpi: int = 300):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=dpi)
    pix.save(png_path)
    doc.close()
