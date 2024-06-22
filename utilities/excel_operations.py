from RPA.Excel.Files import Files as Excel
import os
from pathlib import Path
from robocorp import workitems
from robocorp.tasks import get_output_dir

class ExcelHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.split(self.file_path)[1]
        self.excel = Excel()

    def create_excel_if_not_exists(self, values_dict):
        if not os.path.exists(self.file_path):
            self.excel.create_workbook(self.file_path)
            self.excel.save_workbook(self.file_path)
            self.write_columns_to_excel(values_dict)       
        else:
            raise RuntimeError("Excel workbook already exists.")

    def write_columns_to_excel(self, values_dict):
        self.excel.open_workbook(self.file_path)
        self.excel.create_worksheet("Sheet1")

        # Write headers (column names) from values_dict keys
        columns = list(values_dict.keys())
        for idx, column_name in enumerate(columns, start=1):
            self.excel.set_cell_value(1, idx, column_name)

        self.excel.save_workbook(self.file_path)

    def insert_values_to_excel(self, values_dict, row=2):
        self.workbook = self.excel.open_workbook(self.file_path)
        

        for col_idx, (col_name, col_value) in enumerate(values_dict.items(), start=1):
            self.excel.set_cell_value(row, col_idx, col_value)
        self.excel.save_workbook(self.file_path)
    
    def read_config(self):
        self.excel.open_workbook(self.file_path)
        search_phrase = self.excel.get_cell_value(row=2, column="A")
        category = self.excel.get_cell_value(row=2, column="B")
        number_of_months = self.excel.get_cell_value(row=2, column="C")
        return {"topic":search_phrase, "category":category, "number_of_months":number_of_months}
    
    def load_work_items(self):
        """Split Excel rows into multiple output Work Items for the next step."""
        for item in workitems.inputs:

            excel = Excel()
            excel.open_workbook(self.file_path)
            rows = excel.read_worksheet_as_table(header=True)

            for row in rows:    
                payload = {
                    "search phrase": row["search phrase"],
                    "category": row["category"],
                    "number of months": row["number of months"],
                }
                workitems.outputs.create(payload)

         