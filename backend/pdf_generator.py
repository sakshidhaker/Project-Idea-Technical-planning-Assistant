"""Markdown-ish text -> styled PDF (reportlab)."""
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Preformatted, Paragraph, SimpleDocTemplate, Spacer


def _inline(text):
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)


def build_pdf(title, body, path):
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=colors.HexColor("#4f46e5"), fontSize=22)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=colors.HexColor("#0e7490"))
    txt = ParagraphStyle("t", parent=ss["BodyText"], leading=15)
    code = ParagraphStyle("c", fontName="Courier", fontSize=8.5, leading=11,
                          backColor=colors.HexColor("#f1f5f9"), borderPadding=6, leftIndent=4)
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=title,
                            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story, in_code, buf = [Paragraph(escape(title), h1), Spacer(1, 10)], False, []
    for line in body.splitlines():
        if line.strip().startswith("```"):
            if in_code:
                story += [Preformatted("\n".join(buf), code), Spacer(1, 8)]
                buf = []
            in_code = not in_code
            continue
        if in_code:
            buf.append(line)
        elif line.startswith("#"):
            story += [Spacer(1, 6), Paragraph(_inline(line.lstrip("# ")), h2)]
        elif re.match(r"^\s*[-*] ", line):
            story.append(Paragraph("&bull; " + _inline(re.sub(r"^\s*[-*] ", "", line)), txt))
        elif line.strip():
            story.append(Paragraph(_inline(line), txt))
        else:
            story.append(Spacer(1, 5))
    if buf:
        story.append(Preformatted("\n".join(buf), code))
    doc.build(story)
