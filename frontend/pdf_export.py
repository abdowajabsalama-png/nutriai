"""
NutriAI - PDF Export Service
Generates professional clinical diet plan reports in PDF format.
Supports full Arabic (RTL, font shaping) and English.
"""

import io
import os
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display

# ══════════════════════════════════════════════════════════════════════════════
# FONT REGISTRATION (Windows Native TrueType Fonts)
# ══════════════════════════════════════════════════════════════════════════════

FONTS_INITIALIZED = False

def init_fonts():
    global FONTS_INITIALIZED
    if FONTS_INITIALIZED:
        return

    # Prefer Tahoma on Windows for superior Arabic typography, fallback to Arial/Segoe UI
    reg_candidates = [
        "C:/Windows/Fonts/tahoma.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    bold_candidates = [
        "C:/Windows/Fonts/tahomabd.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
    ]

    font_reg = next((p for p in reg_candidates if os.path.exists(p)), None)
    font_bold = next((p for p in bold_candidates if os.path.exists(p)), font_reg)

    if font_reg:
        pdfmetrics.registerFont(TTFont("NutriArabic", font_reg))
    if font_bold:
        pdfmetrics.registerFont(TTFont("NutriArabicBold", font_bold))

    FONTS_INITIALIZED = True

init_fonts()


import textwrap

# High-precision Arabic Reshaper configuration
reshaper = arabic_reshaper.ArabicReshaper(configuration={
    'delete_harakat': False,
    'support_ligatures': True,
    'RIAL': True,
})

def fix_ar(text: str, is_ar: bool = True, width: int = 44) -> str:
    """
    Reshape and apply bidi algorithm to Arabic text with line-by-line wrapping.
    Wrapping BEFORE BiDi prevents ReportLab from breaking already-reversed lines backwards.
    """
    if not text:
        return ""
    text_str = str(text).strip()
    if not is_ar:
        return text_str
    try:
        # Split by existing newlines if present
        raw_lines = text_str.split('\n')
        wrapped_lines = []
        for r_line in raw_lines:
            r_line = r_line.strip()
            if not r_line:
                continue
            if len(r_line) > width:
                wrapped_lines.extend(textwrap.wrap(r_line, width=width))
            else:
                wrapped_lines.append(r_line)

        # Apply BiDi to each line independently in RTL base direction
        processed = [get_display(reshaper.reshape(line), base_dir='R') for line in wrapped_lines]
        return "<br/>".join(processed)
    except Exception:
        return text_str


def generate_diet_pdf(plan: Dict[str, Any], username: str = "User", language: str = "ar") -> bytes:
    """Generate a high-quality clinical 15-day meal plan PDF."""
    init_fonts()
    is_ar = (language == "ar")
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25,
    )

    styles = getSampleStyleSheet()

    # Style definitions
    align_val = 2 if is_ar else 0  # 2: Right, 0: Left
    center_val = 1

    font_main = "NutriArabic" if is_ar else "Helvetica"
    font_bold = "NutriArabicBold" if is_ar else "Helvetica-Bold"

    style_title = ParagraphStyle(
        "DocTitle",
        fontName=font_bold,
        fontSize=18,
        leading=24,
        textColor=colors.HexColor("#1b5e20"),
        alignment=center_val,
    )

    style_subtitle = ParagraphStyle(
        "DocSubtitle",
        fontName=font_main,
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#388e3c"),
        alignment=center_val,
    )

    style_sec_head = ParagraphStyle(
        "SecHead",
        fontName=font_bold,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1b5e20"),
        alignment=align_val,
        spaceAfter=4,
    )

    style_body = ParagraphStyle(
        "BodyText",
        fontName=font_main,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1f2937"),
        alignment=align_val,
    )

    style_body_bold = ParagraphStyle(
        "BodyTextBold",
        fontName=font_bold,
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#111827"),
        alignment=align_val,
    )

    style_table_header = ParagraphStyle(
        "TableHead",
        fontName=font_bold,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1b5e20"),
        alignment=center_val,
    )

    style_table_cell = ParagraphStyle(
        "TableCell",
        fontName=font_main,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#263238"),
        alignment=align_val,
    )

    style_table_cell_center = ParagraphStyle(
        "TableCellCenter",
        fontName=font_main,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#263238"),
        alignment=center_val,
    )

    story = []

    # ── 1. Document Header ──
    title_text = "🥗 NutriAI - الخطة الغذائية العلاجية المخصصة (15 يوماً)" if is_ar else "🥗 NutriAI - Personalized 15-Day Clinical Nutrition Plan"
    subtitle_text = "تقرير استشاري ذكي مبني على المعايير الغذائية والسريرية" if is_ar else "Evidence-Based Clinical Diet & Macronutrient Assessment"
    
    story.append(Paragraph(fix_ar(title_text, is_ar), style_title))
    story.append(Paragraph(fix_ar(subtitle_text, is_ar), style_subtitle))
    story.append(Spacer(1, 10))

    # Meta bar
    today_str = datetime.now().strftime("%Y-%m-%d")
    meta_text = (
        f"المريض / المستخدم: {username} &nbsp;&nbsp;|&nbsp;&nbsp; تاريخ الإصدار: {today_str} &nbsp;&nbsp;|&nbsp;&nbsp; النظام: NutriAI Clinical v2.0"
        if is_ar else
        f"Patient: {username} &nbsp;&nbsp;|&nbsp;&nbsp; Date: {today_str} &nbsp;&nbsp;|&nbsp;&nbsp; Engine: NutriAI Clinical v2.0"
    )
    story.append(Paragraph(fix_ar(meta_text, is_ar), ParagraphStyle("MetaBar", fontName=font_main, fontSize=9, textColor=colors.HexColor("#555555"), alignment=center_val)))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2e7d32"), spaceAfter=12))

    # ── 2. Profile Summary & Targets ──
    summary = plan.get("user_profile_summary", "")
    if summary:
        lbl_profile = "📌 البيانات الصحية والبدنية الأساسية:" if is_ar else "📌 Patient Health & Metabolic Profile:"
        story.append(Paragraph(fix_ar(lbl_profile, is_ar, width=60), style_sec_head))
        story.append(Paragraph(fix_ar(summary, is_ar, width=82), style_body))
        story.append(Spacer(1, 10))

    # Macros Table
    macros = plan.get("macros", {})
    daily_cal = plan.get("daily_calories", "—")

    lbl_cals = "السعرات اليومية" if is_ar else "Daily Calories"
    lbl_prot = "البروتين" if is_ar else "Protein"
    lbl_carb = "الكربوهيدرات" if is_ar else "Carbohydrates"
    lbl_fat  = "الدهون الصحية" if is_ar else "Healthy Fats"

    val_cals = str(daily_cal)
    val_prot = str(macros.get("protein", "—"))
    val_carb = str(macros.get("carbs", "—"))
    val_fat  = str(macros.get("fat", "—"))

    # For Arabic RTL layout: columns flow Right to Left on paper
    if is_ar:
        macro_headers = [
            Paragraph(fix_ar(lbl_fat, is_ar), style_table_header),
            Paragraph(fix_ar(lbl_carb, is_ar), style_table_header),
            Paragraph(fix_ar(lbl_prot, is_ar), style_table_header),
            Paragraph(fix_ar(lbl_cals, is_ar), style_table_header),
        ]
        macro_values = [
            Paragraph(fix_ar(val_fat, is_ar), style_table_cell_center),
            Paragraph(fix_ar(val_carb, is_ar), style_table_cell_center),
            Paragraph(fix_ar(val_prot, is_ar), style_table_cell_center),
            Paragraph(fix_ar(val_cals, is_ar), style_table_cell_center),
        ]
    else:
        macro_headers = [
            Paragraph(fix_ar(lbl_cals, is_ar), style_table_header),
            Paragraph(fix_ar(lbl_prot, is_ar), style_table_header),
            Paragraph(fix_ar(lbl_carb, is_ar), style_table_header),
            Paragraph(fix_ar(lbl_fat, is_ar), style_table_header),
        ]
        macro_values = [
            Paragraph(fix_ar(val_cals, is_ar), style_table_cell_center),
            Paragraph(fix_ar(val_prot, is_ar), style_table_cell_center),
            Paragraph(fix_ar(val_carb, is_ar), style_table_cell_center),
            Paragraph(fix_ar(val_fat, is_ar), style_table_cell_center),
        ]

    table_macros = Table([macro_headers, macro_values], colWidths=[135, 135, 135, 135])
    table_macros.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f5e9")),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#a5d6a7")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table_macros)
    story.append(Spacer(1, 12))

    # Medical adjustments (Without warning signs)
    adjustments = plan.get("medical_adjustments", [])
    if adjustments:
        lbl_adj = "🩺 التوصيات والإرشادات الطبية المعتمدة في الخطة:" if is_ar else "🩺 Clinical Guidelines & Nutritional Recommendations:"
        story.append(Paragraph(fix_ar(lbl_adj, is_ar, width=60), style_sec_head))
        for adj in adjustments:
            bullet = f"• {adj}"
            story.append(Paragraph(fix_ar(bullet, is_ar, width=82), style_body))
        story.append(Spacer(1, 14))

    # ── 3. 15-Day Meal Plan Table ──
    lbl_plan_head = "📅 جدول الوجبات التفصيلي لـ 15 يوماً:" if is_ar else "📅 Comprehensive 15-Day Meal Schedule:"
    story.append(Paragraph(fix_ar(lbl_plan_head, is_ar, width=60), style_sec_head))
    story.append(Spacer(1, 6))

    meal_plan = plan.get("meal_plan", [])
    meal_type_names = {
        "breakfast": "الإفطار" if is_ar else "Breakfast",
        "lunch":     "الغداء" if is_ar else "Lunch",
        "dinner":    "العشاء" if is_ar else "Dinner",
        "snack":     "سناك" if is_ar else "Snack",
    }

    # Render each day as a clean table with strict RTL / LTR orientation
    for i, day_data in enumerate(meal_plan):
        day_title = day_data.get("day", f"اليوم {i + 1}" if is_ar else f"Day {i + 1}")
        meals = day_data.get("meals", {})

        if is_ar:
            # Arabic layout (Right to Left on paper): [السعرات والملاحظة | تفاصيل الوجبة والمكونات | الوجبة | اليوم]
            day_table_data = [
                [
                    Paragraph(fix_ar("السعرات والملاحظة", is_ar, width=18), style_table_header),
                    Paragraph(fix_ar("تفاصيل الوجبة والمكونات", is_ar, width=44), style_table_header),
                    Paragraph(fix_ar("الوجبة", is_ar, width=14), style_table_header),
                    Paragraph(fix_ar(day_title, is_ar, width=14), ParagraphStyle("DayH", fontName=font_bold, fontSize=10, textColor=colors.HexColor("#1b5e20"), alignment=center_val)),
                ]
            ]

            for m_key in ["breakfast", "lunch", "dinner", "snack"]:
                m_info = meals.get(m_key, {})
                m_label = meal_type_names.get(m_key, m_key)
                m_desc = m_info.get("meal", "")
                m_cal = m_info.get("calories", "")
                m_note = m_info.get("notes", "")
                cal_note_str = f"{m_cal} | {m_note}" if m_note else m_cal

                day_table_data.append([
                    Paragraph(fix_ar(cal_note_str, is_ar, width=16), style_table_cell_center),
                    Paragraph(fix_ar(m_desc, is_ar, width=42), style_table_cell),
                    Paragraph(fix_ar(m_label, is_ar, width=14), style_body_bold),
                    "",  # Right merged day column
                ])

            day_table = Table(day_table_data, colWidths=[105, 290, 70, 75])
            day_table.setStyle(TableStyle([
                ("SPAN", (3, 1), (3, 4)),  # Span the Day column (Column 3 on the right)
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f8e9")),
                ("BACKGROUND", (3, 1), (3, 4), colors.HexColor("#e8f5e9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8e6c9")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (3, 1), (3, 4), "CENTER"),
                ("ALIGN", (2, 1), (2, 4), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
        else:
            # English layout (Left to Right): [Day | Meal | Details | Calories / Notes]
            day_table_data = [
                [
                    Paragraph(fix_ar(day_title, is_ar), ParagraphStyle("DayH", fontName=font_bold, fontSize=10, textColor=colors.HexColor("#1b5e20"), alignment=center_val)),
                    Paragraph(fix_ar("Meal", is_ar), style_table_header),
                    Paragraph(fix_ar("Meal Description & Food Items", is_ar), style_table_header),
                    Paragraph(fix_ar("Calories / Notes", is_ar), style_table_header),
                ]
            ]

            for m_key in ["breakfast", "lunch", "dinner", "snack"]:
                m_info = meals.get(m_key, {})
                m_label = meal_type_names.get(m_key, m_key)
                m_desc = m_info.get("meal", "")
                m_cal = m_info.get("calories", "")
                m_note = m_info.get("notes", "")
                cal_note_str = f"{m_cal} | {m_note}" if m_note else m_cal

                day_table_data.append([
                    "",  # Left merged day column
                    Paragraph(fix_ar(m_label, is_ar), style_body_bold),
                    Paragraph(fix_ar(m_desc, is_ar), style_table_cell),
                    Paragraph(fix_ar(cal_note_str, is_ar), style_table_cell_center),
                ])

            day_table = Table(day_table_data, colWidths=[75, 70, 290, 105])
            day_table.setStyle(TableStyle([
                ("SPAN", (0, 1), (0, 4)),  # Span the Day column (Column 0 on the left)
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f8e9")),
                ("BACKGROUND", (0, 1), (0, 4), colors.HexColor("#e8f5e9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c8e6c9")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 1), (0, 4), "CENTER"),
                ("ALIGN", (1, 1), (1, 4), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))

        story.append(KeepTogether([day_table, Spacer(1, 8)]))

    doc.build(story)
    return buffer.getvalue()
