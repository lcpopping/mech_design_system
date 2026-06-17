"""Import bearing data from Excel to database."""
import os
import xlrd
import sqlite3
from datetime import datetime

# File paths
EXCEL_FILE = "E:/01自动化计算资料大全/机械设计常用计算总目.xls"
DB_FILE = "F:/大开大合/机械设计工具/mech_design_system/data/mech_design.db"


def import_thrust_bearings(wb, cursor):
    """Import thrust bearings from sheet 2 (滚动轴承尺寸查询).

    Columns: 型号|内径d|外径D|宽度T|倒角r|d1|D1|重量ZRO2|重量SI3N4|重量POM|参考型号
    """
    sheet = wb.sheet_by_index(2)  # 滚动轴承尺寸查询
    print(f"\nProcessing thrust bearings sheet: {sheet.nrows} rows")

    count = 0
    for row_idx in range(4, sheet.nrows):  # Skip header rows 0-3
        try:
            model = str(sheet.cell_value(row_idx, 0)).strip()
            if not model or model == '':
                continue

            # Handle bore diameter - some rows have empty bore
            bore = sheet.cell_value(row_idx, 1)
            if isinstance(bore, float) and bore > 0:
                bore_d = bore
            else:
                bore_d = None

            outer_d = sheet.cell_value(row_idx, 2)
            width_t = sheet.cell_value(row_idx, 3)
            chamfer_r = sheet.cell_value(row_idx, 4)

            # Weight - use ZRO2 (ceramic) as default
            weight = sheet.cell_value(row_idx, 7)  # ZRO2 column

            # Parse numeric values
            outer_d = float(outer_d) if outer_d else None
            width_t = float(width_t) if width_t else None
            chamfer_r = float(chamfer_r) if chamfer_r else 0.3
            weight = float(weight) if weight and weight != '' else None

            # Type 4 = thrust ball bearing
            type_id = 4

            # Check if model already exists
            cursor.execute("SELECT id FROM bearings WHERE model = ?", (model,))
            if cursor.fetchone():
                print(f"  Skipping existing: {model}")
                continue

            cursor.execute("""
                INSERT INTO bearings (type_id, model, bore_diameter, outer_diameter, width, weight, standard, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (type_id, model, bore_d, outer_d, width_t, weight, 'GB/T 8592-2001', datetime.now()))
            count += 1
            print(f"  Added thrust bearing: {model}")
        except Exception as e:
            print(f"  Error on row {row_idx}: {e}")

    return count


def import_miniature_bearings(wb, cursor):
    """Import miniature bearings from sheet 3 (平键轴承查询).

    Columns: 型号|内径d|外径D|宽度b|未知|未知|额定动载荷Cr|额定静载荷Cor|最高转速|*1000rpm
    """
    sheet = wb.sheet_by_index(3)  # 平键轴承查询
    print(f"\nProcessing miniature bearings sheet: {sheet.nrows} rows")

    count = 0
    for row_idx in range(3, sheet.nrows):  # Skip header rows 0-2
        try:
            model = str(sheet.cell_value(row_idx, 0)).strip()
            if not model or model == '':
                continue

            # Normalize model name (e.g., 684zz -> 684ZZ)
            model = model.upper().replace('ZZ', 'ZZ')

            bore_d = sheet.cell_value(row_idx, 1)
            outer_d = sheet.cell_value(row_idx, 2)
            width_b = sheet.cell_value(row_idx, 3)

            # Cr and Cor (额定动载荷 and 额定静载荷)
            cr = sheet.cell_value(row_idx, 5)
            cor = sheet.cell_value(row_idx, 6)

            # Max speed - column 7 is in *1000rpm
            max_speed_raw = sheet.cell_value(row_idx, 7)
            max_speed = float(max_speed_raw) * 1000 if max_speed_raw and max_speed_raw != '' else None

            # Parse numeric values
            bore_d = float(bore_d) if bore_d and bore_d != '' else None
            outer_d = float(outer_d) if outer_d and outer_d != '' else None
            width_b = float(width_b) if width_b and width_b != '' else None
            cr = float(cr) if cr and cr != '' else None
            cor = float(cor) if cor and cor != '' else None

            # Type 1 = deep groove ball bearing (微型)
            type_id = 1

            # Check if model already exists
            cursor.execute("SELECT id FROM bearings WHERE model = ?", (model,))
            if cursor.fetchone():
                print(f"  Skipping existing: {model}")
                continue

            cursor.execute("""
                INSERT INTO bearings (type_id, model, bore_diameter, outer_diameter, width,
                                     dynamic_load_rating, static_load_rating, max_speed, standard, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (type_id, model, bore_d, outer_d, width_b, cr, cor, max_speed, 'GB/T 276-2013', datetime.now()))
            count += 1
            print(f"  Added miniature bearing: {model} (d={bore_d}, D={outer_d}, Cr={cr})")
        except Exception as e:
            print(f"  Error on row {row_idx}: {e}")

    return count


def main():
    print("=" * 60)
    print("Importing bearing data from Excel to database")
    print("=" * 60)

    # Open Excel file
    print(f"\nOpening: {EXCEL_FILE}")
    wb = xlrd.open_workbook(EXCEL_FILE, encoding_override='gbk')
    print(f"Sheets: {len(wb.sheet_names())}")

    # Connect to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Get current count
    cursor.execute("SELECT COUNT(*) FROM bearings")
    before_count = cursor.fetchone()[0]
    print(f"\nCurrent bearings in DB: {before_count}")

    # Import thrust bearings (type 4)
    thrust_count = import_thrust_bearings(wb, cursor)

    # Import miniature bearings (type 1)
    mini_count = import_miniature_bearings(wb, cursor)

    # Commit and close
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM bearings")
    after_count = cursor.fetchone()[0]
    print(f"\n{'=' * 60}")
    print(f"Import complete!")
    print(f"  Thrust bearings added: {thrust_count}")
    print(f"  Miniature bearings added: {mini_count}")
    print(f"  Total before: {before_count}")
    print(f"  Total after: {after_count}")
    print(f"  Net new bearings: {after_count - before_count}")
    print(f"{'=' * 60}")

    conn.close()


if __name__ == '__main__':
    main()