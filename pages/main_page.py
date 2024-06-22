
# Enter feature description here

# Enter steps here
import traceback
from utilities import custom_logger as cl
import logging
from datetime import datetime
from RPA.Browser.Selenium import Selenium
from urllib.request import urlretrieve
import random
import os
import re
import time

class MainPage():
    # invoices table
    _reject_cookies_selector = "css:#onetrust-reject-all-handler"
    _open_search_button_selector = "css:.icon--search"
    _search_field_selector = "css:.search-bar__input"
    _search_button_selector = "css:.css-sp7gd"
    _sort_selector = "css:#search-sort-option"
    _news_count = 1
    _news_title_selector = f"xpath:/html/body/div[1]/div/div[3]/div/div/div/div/main/div[2]/div[2]/article[{_news_count}]/div[2]/div[1]/h3/a"
    #_news_title_selector = f"article.gc:nth-child({_news_count}) > div:nth-child(2) > div:nth-child(1) > h3:nth-child(2) > a:nth-child(1) > span"
    _news_description_selector = f"css:article.gc:nth-child({_news_count}) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > p:nth-child(1)"
    _date_selector = f"css:article.gc:nth-child({_news_count}) > div:nth-child(2) > footer:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)"
    _img_selector = f"css:article.gc:nth-child({_news_count}) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > img:nth-child(1)"
    _show_more_selector = "css:.show-more-button > span:nth-child(2)"

    log = cl.customLogger(logging.DEBUG)

    def __init__(self, timeout, images_download_folder_path):
        #self.driver = driver
        self.driver = Selenium()
        self.driver.headless = True
        self.timeout = timeout
        self.images_download_folder_path = images_download_folder_path
    
    def update_dynamic_selectors(self):
        self._news_title_selector = f"xpath:/html/body/div[1]/div/div[3]/div/div/div/div/main/div[2]/div[2]/article[{self._news_count}]/div[2]/div[1]/h3/a"
        self._news_description_selector = f"css:article.gc:nth-child({self._news_count}) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > p:nth-child(1)"
        self._date_selector = f"css:article.gc:nth-child({self._news_count}) > div:nth-child(2) > footer:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)"
        self._img_selector = f"css:article.gc:nth-child({self._news_count}) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > img:nth-child(1)"


    def open_news_website(self, url):
        try:
            chrome_options = {
                "arguments": ["--headless"]
                }
            self.driver.open_browser(url=url, browser="chrome", options=chrome_options)
            #self.driver.maximize_browser_window()
            self.driver.wait_until_element_is_visible(locator=self._reject_cookies_selector, timeout=self.timeout)
            self.driver.click_element(locator=self._reject_cookies_selector)
            self.log.info("Opened news website")
        except Exception as e:
            print(traceback.format_exc())
            self.log.error(f"Failed to open {url} : {traceback.format_exc()}")
            raise Exception("Error searching topic")

    def search_news(self, category, topic):
        """
        Checks if page has loaded, pics category, searches topic
        """
        try:
            category_selector = f"//span[text()='{category}']"
            self.driver.wait_until_element_is_visible(locator=category_selector, timeout=self.timeout)
            self.driver.click_element(locator=category_selector)

            self.driver.wait_until_element_is_visible(locator=self._open_search_button_selector, timeout=self.timeout)
            open_search_element = self.driver.find_element(locator=self._open_search_button_selector)
            self.driver.click_element(locator=open_search_element)

            self.driver.wait_until_element_is_visible(locator=self._search_field_selector, timeout=self.timeout)
            input_element = self.driver.find_element(locator=self._search_field_selector)
            self.driver.input_text(locator=self._search_field_selector, text=topic, clear=True)

            search_button = self.driver.find_element(locator=self._search_button_selector)
            #for retry_count in range(3):
            self.driver.click_element(locator=search_button)
            # Check if news order loaded
            try:
                self.driver.wait_until_element_is_visible(locator=self._news_description_selector, timeout=self.timeout)
                self.driver.find_element(locator=self._sort_selector)
                self.log.info(f"Searched for {topic} in {category} category")
                #break
            except:
                self.log.error("Searched topic didn't load")
                self.driver.driver.refresh()
                time.sleep(3)

        except Exception as e:
            print(traceback.format_exc())
            self.log.error("Error searching topic: " + traceback.format_exc())
            raise Exception("Error searching topic")

    def sort_page(self, sort_option):
        """
        Sort search results
        """
        for retry_count in range(3):
            try:
                self.driver.wait_until_element_is_visible(locator=self._sort_selector, timeout=self.timeout)
                self.driver.wait_until_element_is_enabled(locator=self._sort_selector, timeout=self.timeout)
                self.driver.select_from_list_by_label(self._sort_selector, sort_option)
                self.log.info(f"Page was sorted by {sort_option}")
                # Verify the selected option
                # selected_option =  self.driver.get_selected_list_label(self._sort_selector)
                # print(f"Selected option: {selected_option}")
                # if selected_option != "Date":
                #     raise Exception("Failed to select date")
                break
            except Exception as e:
                print(traceback.format_exc())
                self.log.error("Error sorting the news: " + traceback.format_exc())
                self.driver.driver.refresh()
                if retry_count == 3:
                    raise Exception("Error sorting the news")

    def count_text_occurrences(self, text, sub_text):
        """
        Counts the occurrences of a substring (sub_text) within a larger string (text).
        """
        count = 0
        # Iterate through the larger text with a sliding window the size of the substring
        for i in range(len(text) - len(sub_text) + 1):
            # Check if the current window matches the substring
            if text[i:i+len(sub_text)] == sub_text:
                count += 1
        return count
    
    def has_money(self, text):
        """
        Checks if a text string contains a representation of money.
        """
        # Regex patterns for different money formats
        patterns = [
            r"^\$\d+(?:\.\d{2})?$",  # US dollars (e.g., $11.10)
            r"^\d+(?:,\d{3})*(?:\.\d{2})?$",  # Numbers with commas and optional decimals (e.g., 1,111.11)
            r"\d+ dollars$",  # Numbers followed by "dollars" (e.g., 11 dollars)
            r"\d+ USD$"  # Numbers followed by "USD" (e.g., 11 USD)
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    def check_news_date(self, news_date, requested_period):
        """
        Checks if the news date is within requested period
        """
        valid_news_date = False
        if news_date == "": # Some of the news have empty values for date so we will consider them valid
            valid_news_date = True
            self.log.info("Date is empty")
            return valid_news_date
        else:
            news_date = self.format_date(news_date=news_date)
        current_date = datetime.now()
        # Calculate the difference in months
        difference_in_months = (current_date.year - news_date.year) * 12 + (current_date.month - news_date.month)
        # Check if the difference in months is greater than requested_period
        if difference_in_months > requested_period:
            valid_news_date = False
        else:
            valid_news_date = True
        return valid_news_date

    def format_date(self, news_date):
        """
        Convert string to date
        """
        if "Last update" in news_date:
            date = datetime.strptime(news_date, "Last update %d %b %Y")
        elif "Published On" in news_date:
            date = datetime.strptime(news_date, "Published On %d %b %Y")
        else:
            self.log.debug(f"Unknown date format {news_date}")
            print(news_date)
            date = ""
        return date

    def get_news_info(self, topic, requested_period):
        """
        Get the values: title, date,  description, picture filename
        """
        try:
            if self._news_count%10==0:
                # Click show more results
                self.driver.wait_until_element_is_visible(locator=self._show_more_selector, timeout=self.timeout)
                self.driver.click_element(locator=self._show_more_selector)

            self.update_dynamic_selectors()
            self.driver.wait_until_element_is_visible(locator=self._news_title_selector, timeout=self.timeout)
            news_title_element = self.driver.find_element(locator=self._news_title_selector)
            news_title = news_title_element.text
            
            self.driver.wait_until_element_is_visible(locator=self._news_description_selector)
            news_description_element = self.driver.find_element(locator=self._news_description_selector)
            news_description = news_description_element.text

            try:
                date_element = self.driver.find_element(locator=self._date_selector)
                news_date = date_element.text
            except Exception as e:
                self.log.debug("Failed to get the date")
                print("date not  found")
                news_date = ""

            self.driver.wait_until_element_is_visible(locator=self._img_selector, timeout=self.timeout)
            img_element = self.driver.find_element(locator=self._img_selector)
            img_file_name = self.driver.get_element_attribute(locator=img_element, attribute="alt")
            img_url = self.driver.get_element_attribute(locator=img_element, attribute="src")
            file_name = str(random.randint(100000, 999999)) + ".jpg"
            image_file_path = os.path.join(self.images_download_folder_path, file_name)
            urlretrieve(img_url, image_file_path)

            topic_count = self.count_text_occurrences(text=news_title + " " + news_description, sub_text=topic)

            has_money = str(self.has_money(text=news_title + " " + news_description))

            has_valid_date = self.check_news_date(news_date=news_date, requested_period=requested_period)

            return {"title":news_title, "date":news_date,  "description": news_description, 
                    "picture name":img_file_name,  "topic count":topic_count,  "has money":has_money,
                    "picture file name":file_name, "has valid date":has_valid_date} 

        except Exception as e:
            print(traceback.format_exc())
            self.log.error("Error geting news info: " + traceback.format_exc())
            raise Exception("Error geting news info")




            



