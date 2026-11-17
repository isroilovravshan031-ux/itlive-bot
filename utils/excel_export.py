import os
from datetime import datetime
from typing import List, Dict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

async def export_leads_to_excel(leads: List[dict], output_dir: str = "data/exports") -> str:
    """
    Barcha lidlarni zamonaviy formatlangan Excel (.xlsx) fayliga eksport qiladi
    va fayl manzilini qaytaradi.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"itlive_leads_{timestamp}.xlsx")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ITLive Murojaatlar"

    # Sarlavhalar
    headers = [
        "№ ID",
        "F.I.Sh (Ism)",
        "Telefon raqam",
        "Yoshi",
        "Hudud / Yashash joyi",
        "Qiziqqan kursi",
        "Qulay vaqt",
        "Holati (Status)",
        "Mas'ul sotuvchi",
        "Sotuvchi izohi",
        "Murojaat vaqti",
        "So'nggi o'zgarish"
    ]

    # Stillar
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Dark Navy Blue
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB")
    )

    # Status ranglari
    status_fills = {
        "YANGI": PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid"), # Ko'k
        "BOGLANILDI": PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"), # Sariq
        "YOZILDI": PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid"), # Yashil
        "BEKOR_QILINDI": PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # Qizil
    }

    # Sarlavhani yozish
    ws.row_dimensions[1].height = 28
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = thin_border

    # Ma'lumotlarni yozish
    for row_idx, lead in enumerate(leads, 2):
        ws.row_dimensions[row_idx].height = 22

        status_raw = lead.get("status", "YANGI")
        status_readable = {
            "YANGI": "Yangi murojaat",
            "BOGLANILDI": "Bog'lanildi",
            "YOZILDI": "O'qishga yozildi",
            "BEKOR_QILINDI": "Bekor qilindi"
        }.get(status_raw, status_raw)

        row_data = [
            lead.get("id"),
            lead.get("full_name"),
            lead.get("phone"),
            lead.get("age"),
            lead.get("region"),
            lead.get("course_name") or "Umumiy",
            lead.get("time_preference") or "-",
            status_readable,
            lead.get("sales_person") or "Biriktirilmagan",
            lead.get("sales_notes") or "-",
            str(lead.get("created_at", ""))[:19],
            str(lead.get("updated_at", ""))[:19]
        ]

        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.border = thin_border
            cell.font = Font(name="Calibri", size=10)

            # Markazlashtirish kerak bo'lgan ustunlar: ID, Yosh, Status, Vaqt
            if col_idx in (1, 4, 8, 11, 12):
                cell.alignment = align_center
            else:
                cell.alignment = align_left

            # Status ustuniga rang berish
            if col_idx == 8 and status_raw in status_fills:
                cell.fill = status_fills[status_raw]
                cell.font = Font(name="Calibri", size=10, bold=True)

    # Ustunlar kengligini avtomatik moslashtirish
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(file_path)
    return file_path
