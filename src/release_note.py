from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors

def _make_doc_title(product_type: str, product_name: str, platform: str, version: str) -> str:
    pt = product_type.lower()
    if pt == "fw":
        return f"{product_name} Firmware {version}"
    if pt == "app":
        if platform:
            return f"{product_name} {platform} App {version}"
        return f"{product_name} App {version}"
    if platform:
        return f"{product_name} {platform} SDK {version}"
    return f"{product_name} SDK {version}"


ACCENT = colors.HexColor("#2a7f8f")
LIGHT_ACCENT = colors.HexColor("#e8f4f6")


def _draw_footer(canvas, doc, contact):
    canvas.saveState()
    page_w, _ = A4
    left = doc.leftMargin
    bottom = doc.bottomMargin * 0.55
    col_w = (page_w - doc.leftMargin - doc.rightMargin) / 3

    # Separator line
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.5)
    canvas.line(left, bottom + 30, page_w - doc.rightMargin, bottom + 30)

    # Headers
    canvas.setFont("Helvetica-Bold", 9.5)
    canvas.setFillColor(ACCENT)
    canvas.drawString(left,              bottom + 16, "Email")
    canvas.drawString(left + col_w,      bottom + 16, "Phone")
    canvas.drawString(left + 2 * col_w,  bottom + 16, "Address")

    # Values
    canvas.setFont("Helvetica", 9.5)
    canvas.setFillColor(colors.black)
    canvas.drawString(left,             bottom + 2, contact.get("email", ""))
    canvas.drawString(left + col_w,     bottom + 2, contact.get("phone", ""))

    address_parts = contact.get("address", "").split(", ")
    for i, part in enumerate(address_parts):
        canvas.drawString(left + 2 * col_w, bottom + 2 - i * 12, part)

    canvas.restoreState()


def build_release_note_pdf(
    pdf_path: str,
    platform: str,
    version: str,
    date: str,
    new_functionalities: list,
    enhancements: list,
    previous_versions: list,
    contact: dict,
    product_type: str = "sdk",
    product_name: str = "Wellysis",
    change_categories: list = None,
):
    doc_title = _make_doc_title(product_type, product_name, platform, version)

    style_title    = ParagraphStyle(name="Title",    fontSize=24, leading=30, spaceAfter=10)
    style_subtitle = ParagraphStyle(name="Subtitle", fontSize=13, spaceAfter=6)
    style_normal   = ParagraphStyle(name="Normal",   fontSize=10.5, leading=16, spaceAfter=6)
    style_cat      = ParagraphStyle(name="CatHead",  fontSize=11, leading=14, spaceBefore=0, spaceAfter=0,
                                    textColor=colors.white)
    style_bullet   = ParagraphStyle(name="Bullet",   fontSize=10.5, leading=16, leftIndent=12,
                                    spaceAfter=3, bulletIndent=0)
    style_section  = ParagraphStyle(name="Section",  fontSize=12, spaceBefore=10, spaceAfter=6)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=72,
        rightMargin=72,
        topMargin=80,
        bottomMargin=80,
        title=f"{doc_title} Release Notes"
    )

    W = A4[0] - 144  # usable width
    elements = []

    # ── Header ──────────────────────────────────────────────────────────────
    header = Table(
        [[Paragraph("<b>Wellysis</b>", style_title), Paragraph(f"Date: {date}", style_normal)]],
        colWidths=[4*inch, 2*inch]
    )
    header.setStyle(TableStyle([
        ("ALIGN",         (1, 0), (1, 0), "RIGHT"),
        ("VALIGN",        (0, 0), (-1,-1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1,-1), 0),
        ("RIGHTPADDING",  (0, 0), (-1,-1), 0),
        ("TOPPADDING",    (0, 0), (-1,-1), 0),
        ("BOTTOMPADDING", (0, 0), (-1,-1), 0),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 0.3*inch))

    elements.append(Paragraph(f"<b>{doc_title}</b>", style_subtitle))
    elements.append(Paragraph("<b>Release Notes</b>", style_title))
    elements.append(Paragraph(f"<b>Version:</b> {version}", style_normal))
    elements.append(Paragraph(f"<b>Date:</b> {date}", style_normal))
    elements.append(Spacer(1, 0.1*inch))

    # ── New Functionalities ──────────────────────────────────────────────────
    if new_functionalities:
        elements.append(Paragraph("New Functionalities:", style_section))
        for i, item in enumerate(new_functionalities, 1):
            elements.append(Paragraph(f"{i}. {item}", style_normal))
        elements.append(Spacer(1, 0.2*inch))

    # ── Categorized Changes ──────────────────────────────────────────────────
    if change_categories:
        elements.append(Paragraph("Updates &amp; Improvements:", style_section))
        elements.append(Spacer(1, 0.05*inch))

        for cat in change_categories:
            title_text = cat.get("title", "")
            items      = cat.get("items", [])

            cat_table = Table(
                [[Paragraph(f"<b>{title_text}</b>", style_cat)]],
                colWidths=[W]
            )
            cat_table.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1,-1), ACCENT),
                ("LEFTPADDING",   (0, 0), (-1,-1), 10),
                ("RIGHTPADDING",  (0, 0), (-1,-1), 10),
                ("TOPPADDING",    (0, 0), (-1,-1), 6),
                ("BOTTOMPADDING", (0, 0), (-1,-1), 6),
                ("ROWBACKGROUNDS",(0, 0), (-1,-1), [ACCENT]),
            ]))

            bullet_rows = [[Paragraph(f"• {it}", style_bullet)] for it in items]
            bullet_table = Table(bullet_rows, colWidths=[W])
            bullet_table.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1,-1), LIGHT_ACCENT),
                ("LEFTPADDING",   (0, 0), (-1,-1), 14),
                ("RIGHTPADDING",  (0, 0), (-1,-1), 10),
                ("TOPPADDING",    (0, 0), (-1,-1), 5),
                ("BOTTOMPADDING", (0, 0), (-1,-1), 5),
                ("VALIGN",        (0, 0), (-1,-1), "TOP"),
            ]))

            elements.append(KeepTogether([cat_table, bullet_table, Spacer(1, 0.1*inch)]))

    # ── Legacy flat enhancements (backward compat) ───────────────────────────
    elif enhancements:
        elements.append(Paragraph("Enhancements:", style_section))
        for i, item in enumerate(enhancements, 1):
            elements.append(Paragraph(f"{i}. {item}", style_normal))

    # ── Previous Versions ───────────────────────────────────────────────────
    if previous_versions:
        elements.append(Spacer(1, 0.25*inch))
        elements.append(HRFlowable(color=colors.lightgrey, thickness=1))
        elements.append(Spacer(1, 0.25*inch))
        elements.append(Paragraph("Previous Versions:", style_section))
        pv_rows = []
        for pv in previous_versions:
            v = pv.get("version", "")
            d = pv.get("description", "")
            desc_text = "<br/>".join(f"- {it}" for it in d) if isinstance(d, list) else f"- {d}"
            pv_rows.append([Paragraph(f"<b>{v}</b>", style_normal), Paragraph(desc_text, style_normal)])

        pv_table = Table(pv_rows, colWidths=[1.2*inch, 4.8*inch])
        pv_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1,-1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1,-1), 0),
            ("RIGHTPADDING",  (0, 0), (-1,-1), 0),
            ("TOPPADDING",    (0, 0), (-1,-1), 4),
            ("BOTTOMPADDING", (0, 0), (-1,-1), 4),
        ]))
        elements.append(pv_table)

    # Footer is drawn via canvas callback — pinned to page bottom
    doc.build(
        elements,
        onFirstPage=lambda c, d: None,
        onLaterPages=lambda c, d: _draw_footer(c, d, contact),
    )
