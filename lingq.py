from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium import webdriver
import os
import time
import re

# Load environment variables
load_dotenv()
USERNAME = os.getenv('LINGQ_USERNAME')
PASSWORD = os.getenv('LINGQ_PASSWORD')

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('--start-maximized')
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

# Function to sanitize lesson name to be a valid file name
def sanitize_lesson_name(lesson_name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', lesson_name)


def save_progress(index, lesson_name):
    with open(f"{lesson_name}_progress.txt", "w") as f:
        f.write(str(index))


def load_progress(lesson_name):
    file_name = f"{lesson_name}_progress.txt"
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("0")
    with open(file_name, "r") as f:
        return int(f.read().strip())

def lingq_automater():
    driver.get('https://www.lingq.com/en/accounts/login/')
    time.sleep(5)
    email_field = driver.find_element(By.XPATH, "//div[@class='email-field field']/div/input[@id='id_username']")
    time.sleep(1)
    password_field = driver.find_element(By.XPATH, "//div[@class='email-field field']/div/input[@id='id_password']")
    for char in USERNAME:
        email_field.send_keys(char)
    for char in PASSWORD:
        password_field.send_keys(char)
    time.sleep(2)
    login_button = driver.find_element(By.XPATH, "//button[@id='submit-button']")
    time.sleep(1)
    login_button.click()
    time.sleep(5)
    imp_lesson = driver.find_element(By.XPATH, "//a[.='Imported Lessons']")
    imp_lesson.click()
    time.sleep(4)
    my_lessons = driver.find_elements(By.XPATH, "//div[@class='library-sections--item item--my_lessons']//a[@class='library-item library-item--lesson grid-layout has-background-white box is-paddingless is-shadowless']")
    
    for my_lesson in my_lessons:
        lesson_name = sanitize_lesson_name(my_lesson.text)  
        my_lesson.click()
        time.sleep(5)

        try:
            options_button = driver.find_element(By.XPATH, "//button[@aria-controls='lesson-menu']")
            options_button.click()
            edit_button = driver.find_element(By.XPATH, "//a[.='Edit Lesson']")
            edit_button.click()
            time.sleep(8)
            para_texts = driver.find_elements(By.XPATH, "//div[@class='paragraph-editor grid-layout grid-gap-half'][position() > 1]//span[@data-text='true']")
            time.sleep(4)

            start_index = load_progress(lesson_name)

            for i in range(start_index, len(para_texts)):
                try:
                    para_text = para_texts[i]
                    itr_text = para_text.text
                    if itr_text != '-----':
                        while True:
                            try:
                                i += 1
                                para_text = para_texts[i]
                                itr_text = para_text.text
                                if itr_text == '-----':
                                    break
                                else:
                                    driver.execute_script("arguments[0].scrollIntoView();", para_text)
                                    time.sleep(1)
                                    driver.execute_script("arguments[0].click();", para_text)
                                    time.sleep(3)
                                    remove_spacing = driver.find_element(By.XPATH, "//button[.='Remove paragraph spacing']")
                                    driver.execute_script("arguments[0].scrollIntoView();", remove_spacing)
                                    time.sleep(1)
                                    driver.execute_script("arguments[0].click();", remove_spacing)
                                    time.sleep(6)
                            except IndexError:
                                break
                    save_progress(i, lesson_name)  
                except StaleElementReferenceException:
                    para_texts = driver.find_elements(By.XPATH, "//div[@class='paragraph-editor grid-layout grid-gap-half'][position() > 1]//span[@data-text='true']")
                except NoSuchElementException as e:
                    print(f"An error occurred: {e}")
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
            pass

lingq_automater()
