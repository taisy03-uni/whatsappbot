"""
Alright is unofficial Python wrapper for whatsapp web made as an inspiration from PyWhatsApp
allowing you to send messages, images, video and documents programmatically using Python
"""


import os
import sys
import time
import logging
from typing import Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoSuchElementException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
from pathlib import Path

LOGGER = logging.getLogger()

class WhatsApp(object):
    def __init__(self, browser=None, time_out=600):
        # CJM - 20220419: Added time_out=600 to allow the call with less than 600 sec timeout
        # web.open(f"https://web.whatsapp.com/send?phone={phone_no}&text={quote(message)}")

        self.BASE_URL = "https://web.whatsapp.com/"
        self.suffix_link = "https://web.whatsapp.com/send?phone={mobile}&text&type=phone_number&app_absent=1"

        if not browser:
            service = Service(ChromeDriverManager().install())
            chrome_options = self.chrome_options
            browser = webdriver.Chrome(
                service=service,
                options=chrome_options
            )

            handles = browser.window_handles
            for _, handle in enumerate(handles):
                if handle != browser.current_window_handle:
                    browser.switch_to.window(handle)
                    browser.close()

        self.browser = browser
        # CJM - 20220419: Added time_out=600 to allow the call with less than 600 sec timeout
        self.wait = WebDriverWait(self.browser, time_out)
        self.cli()
        self.login()
        self.mobile = ""

    @property
    def chrome_options(self):
        chrome_options = Options()
        if sys.platform == "win32":
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
        else:
            chrome_options.add_argument("start-maximized")
            chrome_options.add_argument("--user-data-dir=./User_Data")
        return chrome_options

    def cli(self):
        """
        LOGGER settings  [nCKbr]
        """
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s -- [%(levelname)s] >> %(message)s"
            )
        )
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)

    def login(self):
        self.browser.get(self.BASE_URL)
        self.browser.maximize_window()

    def logout(self):
        prefix = "//div[@id='side']/header/div[2]/div/span/div[3]"
        dots_button = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"{prefix}/div[@role='button']",
                )
            )
        )
        dots_button.click()

        logout_item = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f"{prefix}/span/div[1]/ul/li[last()]/div[@role='button']",
                )
            )
        )
        logout_item.click()

    
    def find_unread_messages_direct(self):
        """Finds unread messages and updates people.json"""
        unread_messages = []
        json_file = "people.json"
        
        # Load existing data or create empty structure
        with open(json_file, 'r') as f:
            people_data = json.load(f)

        
        try:
            # Find all chat panels in the sidebar
            chat_panels = self.browser.find_elements(
                By.XPATH, "//div[contains(@class, 'x1016tqk') or contains(@role, 'listitem')]"
            )

            for panel in chat_panels:
                try:
                    # Check if this panel has an unread indicator
                    unread_indicator = panel.find_element(
                        By.XPATH, ".//span[contains(@aria-label, 'unread message')]"
                    )
                    
                    # Extract info if unread messages exist
                    aria_label = unread_indicator.get_attribute('aria-label')
                    unread_count = int(aria_label.split()[0])
                    
                    sender_element = panel.find_element(
                        By.XPATH, ".//span[@title or @dir='auto']"
                    )
                    sender_name = sender_element.get_attribute('title') or sender_element.text
                    
                    preview_element = panel.find_element(
                        By.XPATH, ".//span[@dir='ltr']"
                    )
                    preview_text = preview_element.text
                    
                    # Add to unread messages list
                    unread_messages.append({
                        'sender': sender_name,
                        'preview': preview_text,
                        'unread_count': unread_count,
                        'element': panel
                    })
                    
                    # Update JSON data
                    person_exists = False
                    for person in people_data:
                        if person['name'] == sender_name:
                            person_exists = True
                            # Add message if not already present
                            if preview_text not in person['messages_from']:
                                person['messages_from'].append(preview_text)
                            break
                    
                    if not person_exists:
                        people_data.append({
                            'name': sender_name,
                            'messages_from': [preview_text],
                            'messages_to': []
                        })
                    
                except NoSuchElementException:
                    continue
                    
            # Save updated data to JSON file
            with open(json_file, 'w') as f:
                json.dump(people_data, f, indent=2)
                
        except Exception as e:
            LOGGER.error(f"Error in direct method: {e}")
            
        return unread_messages
    
    def send_message(self):
        unread_messages = self.find_unread_messages_direct()
        if unread_messages:
            unread_messages = unread_messages[0]
        return unread_messages
    
    def send_message_to_chat(self, chat_info, message="I am testing a chatbot, apologies if this message has reached you! It was not meant to."):
        """Opens a chat and sends a message to the specified user"""
        try:
            # Click on the chat element to open it
            chat_info['element'].click()
            time.sleep(2)  # Wait for chat to load
            
            # Find the message input box
            input_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@role='textbox' and @aria-label='Type a message']")
                )
            )
            
            # Clear any existing text (just in case)
            input_box.click()
            time.sleep(0.5)
            
            # Type the message
            input_box.send_keys(message)
            time.sleep(0.5)
            
            # Find and click the send button
            send_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@aria-label='Send']")
                )
            )
            send_button.click()
            
            LOGGER.info(f"Message sent to {chat_info['sender']}")
            return True
            
        except Exception as e:
            LOGGER.error(f"Failed to send message to {chat_info['sender']}: {e}")
            return False