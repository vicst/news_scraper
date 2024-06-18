from RPA.Excel.Files import Files as Excel
import os

class ExcelHandler:
    def __init__(self, filename):
        self.filename = filename
        self.excel = Excel()

    def create_excel_if_not_exists(self, values_dict):
        if not os.path.exists(self.filename):
            self.excel.create_workbook(self.filename)
            self.excel.save_workbook(self.filename)
            self.write_columns_to_excel(values_dict)       
        else:
            raise RuntimeError("Excel workbook already exists.")

    def write_columns_to_excel(self, values_dict):
        self.excel.open_workbook(self.filename)
        self.excel.create_worksheet("Sheet1")

        # Write headers (column names) from values_dict keys
        columns = list(values_dict.keys())
        for idx, column_name in enumerate(columns, start=1):
            self.excel.set_cell_value(1, idx, column_name)

        self.excel.save_workbook(self.filename)

    def insert_values_to_excel(self, values_dict, row=2):
        self.workbook = self.excel.open_workbook(self.filename)
        

        for col_idx, (col_name, col_value) in enumerate(values_dict.items(), start=1):
            self.excel.set_cell_value(row, col_idx, col_value)
        self.excel.save_workbook(self.filename)
    
    def read_config(self):
        self.excel.open_workbook(self.filename)
        search_phrase = self.excel.get_cell_value(row=2, column="A")
        category = self.excel.get_cell_value(row=2, column="B")
        number_of_months = self.excel.get_cell_value(row=2, column="C")
        return {"topic":search_phrase, "category":category, "number_of_months":number_of_months}

         