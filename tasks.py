from RPA.Browser.Selenium import Selenium
from datetime import date, datetime
import os
from pages import main_page
from utilities import custom_logger as cl
from utilities.excel_operations import ExcelHandler
from robocorp.tasks import task
from pathlib import Path
import logging
import traceback
from robocorp import workitems


class scrape_news:
    _output_dir = Path(os.environ.get('ROBOT_ARTIFACTS'))
    log = cl.customLogger(logging.DEBUG)

    def __init__(self, input_file, url) -> None:
        self.url = url
        self.category = None
        self.topic = None
        self.requested_period = None
        self.current_date = datetime.now().strftime("%m%d%y_%M")
        self.driver = Selenium()
        self.reports_folder_path = os.path.join(self._output_dir, "Reports")
        self.images_download_folder_path = os.path.join(self._output_dir, "Images")
        self.report_path = os.path.join(self.reports_folder_path,
                                        "report_{}.xlsx".format(self.current_date))
        self.input_files_folder_path = os.path.join(os.path.dirname(__file__), "input_files")
        self.input_file = input_file
        self.input_file_path =  os.path.join(self.input_files_folder_path, self.input_file)
        self.report_columns = ["title", "date", "description", "picture_filename", "search_phrases_count",
                            "has_money"]
        self.main_page = main_page.MainPage(timeout=15, images_download_folder_path = self.images_download_folder_path)
        
    def read_requirements(self, work_item):
        try:
            self.topic =  work_item.payload["search phrase"]
            self.category = work_item.payload["category"]
            self.requested_period = work_item.payload["number of months"]
        except KeyError as err:
            work_item.fail("APPLICATION", code="MISSING_FIELD", message=str(err))
            self.log.error(f"Failed to read work item {str(err)}" )
            raise "Failed to read work item"

    def run_scrape(self, work_item):
        self.log.info("===Process start===")
        self.read_requirements(work_item)
        if not os.path.exists(self.reports_folder_path):
            os.mkdir(self.reports_folder_path)
        if not os.path.exists(self.images_download_folder_path):
            os.mkdir(self.images_download_folder_path)
        
        excel_handler = ExcelHandler(file_path=self.report_path)
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
        self.log.info("===Process end===")

scraper = scrape_news(input_file="FindNewsInput.xlsx" ,
                url="https://www.aljazeera.com/")
@task      
def main():
    for work_item in workitems.inputs:
        try:
            scraper.run_scrape(work_item)
            work_item.done()
        except Exception as e:
            work_item.fail("APPLICATION", code="FAILED_SCRAPE", message=str(e))
            scraper.log.error(f"!!!Failed to run scrape!!! {traceback.format_exc()}")


@task
def producer():
    ExcelHandler(file_path=scraper.input_file_path).load_work_items()