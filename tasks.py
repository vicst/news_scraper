from RPA.Browser.Selenium import Selenium
from datetime import date, datetime
import os
import win32com.client
from pages import main_page
from RPA.Excel.Files import Files as Excel
from utilities.custom_logger import customLogger as cl
from utilities.excel_operations import ExcelHandler


class scrape_news:
    def __init__(self, input_file, url) -> None:
        self.url = url
        self.category = None
        self.topic = None
        self.requested_period = None
        self.current_date = datetime.now().strftime("%m%d%y_%M")
        self.driver = Selenium()
        self.reports_folder_path = os.path.join(os.path.dirname(__file__),"output", "Reports")
        self.images_download_folder_path = os.path.join(os.path.dirname(__file__),"output", "Images")
        self.report_path = os.path.join(os.path.dirname(__file__), self.reports_folder_path,
                                        "report_{}.xlsx".format(self.current_date))
        self.input_files_folder_path = os.path.join(os.path.dirname(__file__), "input_files")
        self.input_file = input_file
        self.input_file_path =  os.path.join(self.input_files_folder_path, self.input_file)
        self.report_columns = ["title", "date", "description", "picture_filename", "search_phrases_count",
                            "has_money"]
        self.main_page = main_page.MainPage(timeout=15, images_download_folder_path = self.images_download_folder_path)
        
    def read_requirements(self):
        input_info = ExcelHandler(filename=self.input_file_path).read_config()
        self.topic =  input_info["topic"]
        self.category = input_info["category"]
        self.requested_period = input_info["number_of_months"]
            

    def run_scrape(self):
        self.read_requirements()
        if not os.path.exists(self.reports_folder_path):
            os.mkdir(self.reports_folder_path)
        if not os.path.exists(self.images_download_folder_path):
            os.mkdir(self.images_download_folder_path)
        xl = win32com.client.Dispatch("Excel.Application")
        xl.Quit()  # close excel if opened  
        
        excel_handler = ExcelHandler(self.report_path)
        self.main_page.open_news_website(url=self.url)
        self.main_page.search_news(category=self.category, topic=self.topic)
        self.main_page.sort_page("Date")
        valid_date = True
        while valid_date:
            news_info = self.main_page.get_news_info(topic=self.topic, requested_period=self.requested_period)
            valid_date = news_info["has valid date"]
            if not valid_date:
                break
            if not os.path.exists(self.report_path):
                excel_handler.create_excel_if_not_exists(news_info)
            news_info.pop("has valid date") 
            excel_handler.insert_values_to_excel(news_info, row=self.main_page._news_count + 1)
            self.main_page._news_count += 1
            print(self.main_page._news_count)

@task        
def main():
    scrape_news(input_file="FindNewsInput.xlsx" ,
                url="https://www.aljazeera.com/").run_scrape()


if __name__ == "__main__":
    main()

