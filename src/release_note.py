from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors

def _make_doc_title(product_type: str, product_name: str, platform: str, version: str) -> str:
    """Compose the subtitle line above 'Release Notes' heading."""
    pt = product_type.lower()
    if pt == "fw":
        return f"{product_name} Firmware {version}"
    if pt == "app":
        if platform:
            return f"{product_name} {platform} App {version}"
        return f"{product_name} App {version}"
    # sdk (default)
    if platform:
        return f"{product_name} {platform} SDK {version}"
    return f"{product_name} SDK {version}"


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
):
    doc_title = _make_doc_title(product_type, product_name, platform, version)

    title = ParagraphStyle(name="Title", fontSize=24, leading=30, spaceAfter=10)
    subtitle = ParagraphStyle(name="Subtitle", fontSize=13, spaceAfter=6)
    section = ParagraphStyle(name="Section", fontSize=12, spaceBefore=16, spaceAfter=8)
    normal = ParagraphStyle(name="Normal", fontSize=10.5, leading=16, spaceAfter=6)
    footer_head = ParagraphStyle(name="FooterHead", fontSize=9.5, textColor=colors.HexColor("#2a7f8f"))
    footer_text = ParagraphStyle(name="FooterText", fontSize=9.5, leading=14)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=72,
        rightMargin=72,
        topMargin=80,
        bottomMargin=80,
        title=f"{doc_title} Release Notes"
    )

    elements = []

    # Header: Wellysis (left) + Date (right)
    header = Table(
        [[Paragraph("<b>Wellysis</b>", title), Paragraph(f"Date: {date}", normal)]],
        colWidths=[4*inch, 2*inch]
    )
    header.setStyle(TableStyle([
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 0.4*inch))

    elements.append(Paragraph(f"<b>{doc_title}</b>", subtitle))
    elements.append(Paragraph("<b>Release Notes</b>", title))

    elements.append(Paragraph(f"<b>Version:</b> {version}", normal))
    elements.append(Paragraph(f"<b>Date:</b> {date}", normal))

    # New Functionalities (hidden when empty)
    if new_functionalities:
        elements.append(Paragraph("New Functionalities:", section))
        for i, item in enumerate(new_functionalities, 1):
            elements.append(Paragraph(f"{i}. {item}", normal))
        elements.append(Spacer(1, 0.2*inch))

    # Enhancements (hidden when empty)
    if enhancements:
        elements.append(Paragraph("Enhancements:", section))
        for i, item in enumerate(enhancements, 1):
            elements.append(Paragraph(f"{i}. {item}", normal))

    elements.append(Spacer(1, 0.25*inch))
    elements.append(HRFlowable(color=colors.lightgrey, thickness=1))
    elements.append(Spacer(1, 0.25*inch))

    # Previous Versions
    elements.append(Paragraph("Previous Versions:", section))

    # Expect list of dicts: {version, description}
    pv_rows = []
    for pv in previous_versions:
        v = pv.get("version", "")
        d = pv.get("description", "")
        pv_rows.append([Paragraph(f"<b>{v}</b>", normal), Paragraph(f"- {d}", normal)])

    pv_table = Table(pv_rows, colWidths=[1.2*inch, 4.8*inch])
    pv_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elements.append(pv_table)

    elements.append(Spacer(1, 0.2*inch))
    elements.append(HRFlowable(color=colors.lightgrey, thickness=1))

    # Footer 3 columns
    elements.append(Spacer(1, 0.6*inch))
    footer = Table([
        [
            Paragraph("<b>Email</b>", footer_head),
            Paragraph("<b>Phone</b>", footer_head),
            Paragraph("<b>Address</b>", footer_head),
        ],
        [
            Paragraph(contact.get("email", ""), footer_text),
            Paragraph(contact.get("phone", ""), footer_text),
            Paragraph(contact.get("address", "").replace(", ", ",<br/>") , footer_text),
        ]
    ], colWidths=[2*inch,2*inch,2*inch])

    footer.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))

    elements.append(footer)

    doc.build(elements)
