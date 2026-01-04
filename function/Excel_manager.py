import openpyxl
import win32com.client as win32
import os

class Excel_Manager:
    def __init__(self):
        pass

    def read_excel(self, file_path):
        """
        Reads an Excel file using openpyxl and returns data.
        """
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook.active
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(row)
            return data
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return []

    def write_excel_template(self, template_path, output_path, data_map):
        """
        Writes data to an Excel file using a template and win32com.
        data_map: dict where key is cell address (e.g., 'A1') and value is content.
        """
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            return

        try:
            excel = win32.gencache.EnsureDispatch('Excel.Application')
            excel.Visible = False
            wb = excel.Workbooks.Open(os.path.abspath(template_path))
            ws = wb.Worksheets(1)

            for cell, value in data_map.items():
                ws.Range(cell).Value = value

            wb.SaveAs(os.path.abspath(output_path))
            wb.Close()
            excel.Quit()
            print(f"File saved to: {output_path}")
        except Exception as e:
            print(f"Error writing Excel file with win32: {e}")
