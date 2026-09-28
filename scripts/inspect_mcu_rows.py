import os
import sys
import openpyxl
import config

if len(sys.argv) < 2:
    print(f"[-] Error: Missing required file path argument.")
    print(f"[*] Usage: python {os.path.basename(sys.argv[0])} <path_to_excel_file.xlsx>")
    sys.exit(1)

path = sys.argv[1]

if not os.path.exists(path):
    print(f"[-] Error: File not found: {path}")
    sys.exit(1)
wb = openpyxl.load_workbook(path, data_only=True)
sheet = wb.active

headers = [str(cell).strip() if cell is not None else f"Col{idx}" for idx, cell in enumerate(next(sheet.iter_rows(values_only=True)), start=1)]

print(f"Headers: {headers}")

print("\n--- Rows 70 to 120 ---")
for r_idx in range(70, 121):
    row_cells = [cell.value for cell in sheet[r_idx]]
    # Get columns of interest
    ident = row_cells[headers.index("id")] if "id" in headers else ""
    title = row_cells[headers.index("Primary Text")] if "Primary Text" in headers else ""
    shape = row_cells[headers.index("Artifact Type")] if "Artifact Type" in headers else ""
    section = row_cells[headers.index("section")] if "section" in headers else ""
    is_heading = row_cells[headers.index("isHeading")] if "isHeading" in headers else ""
    
    print(f"Row {r_idx:3d} | ID: {str(ident):8s} | Type: {str(shape):20s} | Section: {str(section):10s} | IsHeading: {str(is_heading):5s} | Text: {str(title)[:100]}")
