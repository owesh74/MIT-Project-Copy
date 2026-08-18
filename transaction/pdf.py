"""
Server-side PDF generation for Invoices and Quotations.

Everything drawn here is pulled live from the database at request time
(Invoice / InvoiceLineItem / Quotation / QuotationLineItem / CompanyProfile /
Client). Nothing is hardcoded — if a record is edited, the next download
reflects the new values automatically.
"""

import io
import os

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Table, TableStyle, Paragraph, Spacer, Image, KeepTogether,
)

# -----------------------------------------------------------------
# Fonts (bundled so the Rupee symbol "₹" always renders correctly,
# regardless of what fonts are installed on the server / dev machine)
# -----------------------------------------------------------------

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")

_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(FONTS_DIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Oblique", os.path.join(FONTS_DIR, "DejaVuSans-Oblique.ttf")))
    _FONTS_REGISTERED = True


_register_fonts()

FONT_REGULAR = "DejaVuSans"
FONT_BOLD = "DejaVuSans-Bold"
FONT_ITALIC = "DejaVuSans-Oblique"

# -----------------------------------------------------------------
# Brand palette (matched to the MIT NEXT quote samples)
# -----------------------------------------------------------------

GREEN = colors.HexColor("#1E8449")
LIGHT_GREEN = colors.HexColor("#E8F5EC")
GREY_ROW = colors.HexColor("#F2F2F2")
HIGHLIGHT = colors.HexColor("#FFD966")
DARK_TEXT = colors.HexColor("#1a1a1a")

PAGE_SIZE = A4
PAGE_W, PAGE_H = PAGE_SIZE
MARGIN = 16 * mm
BORDER_INSET = 4 * mm


# -----------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------

def _rupees(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0
    return "\u20b9 {:,.2f}".format(value)


def _fmt_date(value):
    if not value:
        return "-"
    try:
        return value.strftime("%d-%m-%Y")
    except AttributeError:
        return str(value)


def _company_logo_flowable(company, max_w=26 * mm, max_h=26 * mm):
    logo = getattr(company, "company_logo", None)
    if not logo:
        return None
    try:
        if not logo.name:
            return None
        path = logo.path
        if not os.path.exists(path):
            return None
        img = Image(path)
        ratio = img.imageWidth / float(img.imageHeight)
        if ratio >= 1:
            img.drawWidth = max_w
            img.drawHeight = max_w / ratio
        else:
            img.drawHeight = max_h
            img.drawWidth = max_h * ratio
        return img
    except Exception:
        return None


def _draw_border(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(1.6)
    canvas.rect(
        BORDER_INSET,
        BORDER_INSET,
        PAGE_W - 2 * BORDER_INSET,
        PAGE_H - 2 * BORDER_INSET,
    )
    canvas.restoreState()


def _styles():
    return {
        "company_name": ParagraphStyle(
            "company_name", fontName=FONT_BOLD, fontSize=17,
            textColor=GREEN, leading=19,
        ),
        "company_sub": ParagraphStyle(
            "company_sub", fontName=FONT_REGULAR, fontSize=8,
            textColor=colors.HexColor("#c0392b"), leading=10,
        ),
        "company_info": ParagraphStyle(
            "company_info", fontName=FONT_REGULAR, fontSize=8.5,
            textColor=DARK_TEXT, leading=11,
        ),
        "doc_heading": ParagraphStyle(
            "doc_heading", fontName=FONT_BOLD, fontSize=30,
            textColor=GREEN, alignment=TA_RIGHT, leading=32,
        ),
        "section_header": ParagraphStyle(
            "section_header", fontName=FONT_BOLD, fontSize=9.5,
            textColor=colors.white, leading=12,
        ),
        "body": ParagraphStyle(
            "body", fontName=FONT_REGULAR, fontSize=8.5,
            textColor=DARK_TEXT, leading=11,
        ),
        "body_bold": ParagraphStyle(
            "body_bold", fontName=FONT_BOLD, fontSize=8.5,
            textColor=DARK_TEXT, leading=11,
        ),
        "cell": ParagraphStyle(
            "cell", fontName=FONT_REGULAR, fontSize=8.2,
            textColor=DARK_TEXT, leading=10.5,
        ),
        "cell_center": ParagraphStyle(
            "cell_center", fontName=FONT_REGULAR, fontSize=8.2,
            textColor=DARK_TEXT, leading=10.5, alignment=TA_CENTER,
        ),
        "cell_right": ParagraphStyle(
            "cell_right", fontName=FONT_REGULAR, fontSize=8.2,
            textColor=DARK_TEXT, leading=10.5, alignment=TA_RIGHT,
        ),
        "footer": ParagraphStyle(
            "footer", fontName=FONT_REGULAR, fontSize=8,
            textColor=DARK_TEXT, alignment=TA_CENTER, leading=11,
        ),
        "footer_thanks": ParagraphStyle(
            "footer_thanks", fontName=FONT_ITALIC, fontSize=10.5,
            textColor=DARK_TEXT, alignment=TA_CENTER, leading=14,
        ),
        "small_label": ParagraphStyle(
            "small_label", fontName=FONT_BOLD, fontSize=8,
            textColor=DARK_TEXT, leading=10,
        ),
    }


def _info_box(rows, styles, label_w=32 * mm, value_w=28 * mm):
    """Small bordered DATE / NUMBER / VALID-UNTIL style box, top right."""
    data = []
    for label, value in rows:
        data.append([
            Paragraph(label, styles["small_label"]),
            Paragraph(str(value), styles["body"]),
        ])
    t = Table(data, colWidths=[label_w, value_w])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _header_block(doc_label, company, info_rows, styles):
    """Top header: logo + company info on the left, big heading + info box on the right."""

    logo = _company_logo_flowable(company, max_w=48 * mm, max_h=22 * mm)

    address_lines = []
    if company.address:
        address_lines.append(company.address.replace("\n", "<br/>"))
    city_line = ", ".join([p for p in [company.city, company.state] if p])
    if city_line:
        pincode = f", {company.pincode}" if company.pincode else ""
        address_lines.append(f"{city_line}{pincode}")
    if company.website:
        address_lines.append(f"Website: {company.website}")
    if company.phone:
        address_lines.append(f"Phone: {company.phone}")
    if company.gst_number:
        address_lines.append(f"GST No.: {company.gst_number}")

    address_para = Paragraph("<br/>".join(address_lines), styles["company_info"])

    if logo:
        # The logo image already carries the company name/branding, so we
        # don't repeat it as a large duplicate heading — just the logo
        # stacked above the address/contact details, both left-aligned.
        logo.hAlign = "LEFT"
        left_cells = [logo, Spacer(1, 6), address_para]
    else:
        left_cells = [
            Paragraph(company.company_name or "Company Name", styles["company_name"]),
            address_para,
        ]

    right_cells = [
        Paragraph(doc_label, styles["doc_heading"]),
        Spacer(1, 6),
        _info_box(info_rows, styles),
    ]

    header_table = Table(
        [[left_cells, right_cells]],
        colWidths=[105 * mm, 68 * mm],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return header_table



def _green_bar(text, styles, width=None):
    t = Table([[Paragraph(text, styles["section_header"])]], colWidths=[width] if width else None)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    t.hAlign = "LEFT"
    return t


def _customer_block(client, extra_id_line, styles):
    lines = [f"<b>{client.client_name}</b>"]
    if client.company_name:
        lines.append(client.company_name)
    if client.address:
        lines.append(client.address.replace("\n", "<br/>"))
    city_line = ", ".join([p for p in [client.city, client.state] if p])
    if city_line:
        lines.append(city_line)
    if client.gst_number:
        lines.append(f"GST No.: {client.gst_number}")

    bar = _green_bar("CUSTOMER", styles, width=95 * mm)
    body = Paragraph("<br/>".join(lines), styles["body"])
    return KeepTogether([bar, Spacer(1, 3), body])


def _bank_details_block(company, for_line, styles):
    left_lines = [
        "<b>Account Holder:</b> " + (company.company_name or "-"),
        f"<b>Bank Name:</b> {company.bank_name or '-'}",
        f"<b>Acc No.:</b> {company.account_number or '-'}",
        f"<b>IFSC:</b> {company.ifsc_code or '-'}",
    ]

    bar = _green_bar("BANK DETAILS", styles, width=178 * mm)

    left = Paragraph("<br/>".join(left_lines), styles["body"])
    right = Paragraph(
        f"{for_line}<br/><br/><br/>_____________________<br/>Authorized Signatory",
        styles["body"],
    )

    inner = Table([[left, right]], colWidths=[100 * mm, 78 * mm])
    inner.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    return KeepTogether([bar, inner])


def _footer_block(company, styles):
    contact_bits = [b for b in [company.phone, company.email] if b]
    contact = " / ".join(contact_bits) if contact_bits else "us"
    return [
        Spacer(1, 6),
        Paragraph(
            f"If you have any questions, please contact {contact}",
            styles["footer"],
        ),
        Spacer(1, 4),
        Paragraph("Thank You For Your Business!", styles["footer_thanks"]),
    ]


def _make_doc(buffer):
    doc = BaseDocTemplate(
        buffer,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    frame = Frame(
        MARGIN, MARGIN,
        PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN,
        id="main",
    )
    template = PageTemplate(id="bordered", frames=[frame], onPage=_draw_border)
    doc.addPageTemplates([template])
    return doc


# -----------------------------------------------------------------
# QUOTATION PDF
# -----------------------------------------------------------------

def build_quotation_pdf(quotation):

    styles = _styles()
    buffer = io.BytesIO()
    doc = _make_doc(buffer)
    story = []

    company = quotation.company
    client = quotation.client

    info_rows = [
        ("DATE", _fmt_date(quotation.quote_date)),
        ("QUOTE #", quotation.quote_number),
        ("CUSTOMER ID", client.id),
        ("VALID UNTIL", _fmt_date(quotation.valid_until)),
    ]

    story.append(_header_block("QUOTE", company, info_rows, styles))
    story.append(Spacer(1, 4))
    if quotation.prepared_by:
        story.append(Paragraph(f"Prepared By: {quotation.prepared_by}", styles["body"]))
    story.append(Spacer(1, 8))
    story.append(_customer_block(client, None, styles))
    story.append(Spacer(1, 10))

    # ---------- item table ----------
    header = [
        Paragraph("Sr", styles["section_header"]),
        Paragraph("Description", styles["section_header"]),
        Paragraph("Qty", styles["section_header"]),
        Paragraph("HSN/SAC", styles["section_header"]),
        Paragraph("Rate", styles["section_header"]),
        Paragraph("Amount", styles["section_header"]),
    ]

    rows = [header]
    items = list(quotation.items.all())
    for idx, item in enumerate(items, start=1):
        rows.append([
            Paragraph(str(idx), styles["cell_center"]),
            Paragraph(item.description or "", styles["cell"]),
            Paragraph(f"{item.quantity:g}" if item.quantity == int(item.quantity) else str(item.quantity), styles["cell_center"]),
            Paragraph(item.hsn_code or "-", styles["cell_center"]),
            Paragraph(_rupees(item.rate), styles["cell_right"]),
            Paragraph(_rupees(item.amount), styles["cell_right"]),
        ])

    col_widths = [9 * mm, 82 * mm, 13 * mm, 22 * mm, 24 * mm, 28 * mm]

    item_table = Table(rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.6, GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for r in range(1, len(rows)):
        if r % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, r), (-1, r), GREY_ROW))
    item_table.setStyle(TableStyle(style_cmds))
    story.append(item_table)
    story.append(Spacer(1, 10))

    # ---------- terms + totals row ----------
    terms_lines = (quotation.terms_and_conditions or "").splitlines()
    terms_html = "<br/>".join(terms_lines) if terms_lines else ""

    terms_block = [
        _green_bar("TERMS AND CONDITIONS", styles, width=100 * mm),
        Spacer(1, 3),
        Paragraph(terms_html, styles["cell"]),
        Spacer(1, 12),
        Paragraph("Customer Acceptance (sign below):", styles["cell"]),
        Spacer(1, 14),
        Paragraph("x ___________________________________", styles["cell"]),
        Paragraph("Print Name:", styles["cell"]),
    ]

    totals_rows = [
        ["Subtotal", _rupees(quotation.subtotal)],
        ["Taxable", _rupees(quotation.taxable_amount)],
        ["Tax rate", f"{quotation.tax_rate:.3f}%"],
        ["Tax due", _rupees(quotation.tax_due)],
        ["Other", _rupees(quotation.other_charges) if quotation.other_charges else "-"],
    ]
    totals_table_rows = [
        [Paragraph(label, styles["body"]), Paragraph(value, styles["cell_right"])]
        for label, value in totals_rows
    ]
    totals_table_rows.append([
        Paragraph("TOTAL", styles["body_bold"]),
        Paragraph(_rupees(quotation.grand_total), styles["body_bold"]),
    ])

    totals_table = Table(totals_table_rows, colWidths=[30 * mm, 32 * mm])
    totals_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, -1), (-1, -1), HIGHLIGHT),
    ]))

    bottom_row = Table(
        [[terms_block, totals_table]],
        colWidths=[110 * mm, 63 * mm],
    )
    bottom_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bottom_row)
    story.append(Spacer(1, 12))

    story.append(_bank_details_block(
        company,
        f"For {company.company_name}",
        styles,
    ))

    story.extend(_footer_block(company, styles))

    doc.build(story)
    buffer.seek(0)
    return buffer


# -----------------------------------------------------------------
# INVOICE PDF
# -----------------------------------------------------------------

def build_invoice_pdf(invoice):

    styles = _styles()
    buffer = io.BytesIO()
    doc = _make_doc(buffer)
    story = []

    company = invoice.company
    client = invoice.client

    info_rows = [
        ("DATE", _fmt_date(invoice.invoice_date)),
        ("INVOICE #", invoice.invoice_number),
        ("CUSTOMER ID", client.id),
        ("STATUS", invoice.status),
    ]

    story.append(_header_block("INVOICE", company, info_rows, styles))
    story.append(Spacer(1, 10))
    story.append(_customer_block(client, None, styles))
    story.append(Spacer(1, 10))

    header = [
        Paragraph("Sr", styles["section_header"]),
        Paragraph("Service Description", styles["section_header"]),
        Paragraph("Qty", styles["section_header"]),
        Paragraph("Rate", styles["section_header"]),
        Paragraph("GST %", styles["section_header"]),
        Paragraph("GST Amt", styles["section_header"]),
        Paragraph("Total", styles["section_header"]),
    ]

    rows = [header]
    items = list(invoice.items.select_related("service").all())
    for idx, item in enumerate(items, start=1):
        service_name = item.service.service_name if item.service_id else ""
        hsn = item.service.hsn_code if item.service_id and item.service.hsn_code else ""
        desc = f"{service_name} (HSN/SAC: {hsn})" if hsn else service_name
        rows.append([
            Paragraph(str(idx), styles["cell_center"]),
            Paragraph(desc, styles["cell"]),
            Paragraph(str(item.quantity), styles["cell_center"]),
            Paragraph(_rupees(item.price), styles["cell_right"]),
            Paragraph(f"{item.gst_percentage:.2f}%", styles["cell_center"]),
            Paragraph(_rupees(item.gst_amount), styles["cell_right"]),
            Paragraph(_rupees(item.total), styles["cell_right"]),
        ])

    col_widths = [8 * mm, 62 * mm, 12 * mm, 22 * mm, 16 * mm, 22 * mm, 26 * mm]

    item_table = Table(rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.6, GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    for r in range(1, len(rows)):
        if r % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, r), (-1, r), GREY_ROW))
    item_table.setStyle(TableStyle(style_cmds))
    story.append(item_table)
    story.append(Spacer(1, 10))

    notes_block = [
        _green_bar("NOTES", styles, width=100 * mm),
        Spacer(1, 3),
        Paragraph((invoice.notes or "-").replace("\n", "<br/>"), styles["cell"]),
        Spacer(1, 16),
        Paragraph("Authorized Signatory", styles["cell"]),
        Paragraph("_____________________", styles["cell"]),
    ]

    totals_rows = [
        ["Subtotal", _rupees(invoice.subtotal)],
        ["GST Total", _rupees(invoice.gst_amount)],
        ["Discount", _rupees(invoice.discount) if invoice.discount else "-"],
    ]
    totals_table_rows = [
        [Paragraph(label, styles["body"]), Paragraph(value, styles["cell_right"])]
        for label, value in totals_rows
    ]
    totals_table_rows.append([
        Paragraph("GRAND TOTAL", styles["body_bold"]),
        Paragraph(_rupees(invoice.grand_total), styles["body_bold"]),
    ])

    totals_table = Table(totals_table_rows, colWidths=[30 * mm, 32 * mm])
    totals_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, -1), (-1, -1), HIGHLIGHT),
    ]))

    bottom_row = Table(
        [[notes_block, totals_table]],
        colWidths=[110 * mm, 63 * mm],
    )
    bottom_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(bottom_row)
    story.append(Spacer(1, 12))

    story.append(_bank_details_block(
        company,
        f"For {company.company_name}",
        styles,
    ))

    story.extend(_footer_block(company, styles))

    doc.build(story)
    buffer.seek(0)
    return buffer