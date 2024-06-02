from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium import webdriver
import os
import time


load_dotenv()
USERNAME = os.getenv('LINGQ_USERNAME')
PASSWORD = os.getenv('LINGQ_PASSWORD')


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('--start-maximized')



def start_driver():
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

driver = start_driver()

def extract_lesson_id(lesson_link):
    return lesson_link.split('/')[-1].strip()

def save_progress(index, lesson_id):
    with open(f"{lesson_id}_progress.txt", "w") as f:
        f.write(str(index))

def load_progress(lesson_id):
    file_name = f"{lesson_id}_progress.txt"
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            f.write("0")
    with open(file_name, "r") as f:
        return int(f.read().strip())

def login():
   
    
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

def lingq_automater():
    global driver
    with open("lesson_links.txt", "r") as f:
        lesson_links = f.readlines()
    for index, lesson_link in enumerate(lesson_links):
        if ",completed" in lesson_link:
            continue
        
        lesson_link = lesson_link.strip()
        lesson_id = extract_lesson_id(lesson_link)
        
        driver.get(lesson_link)
        time.sleep(2)
        if "login" in driver.current_url:
            login()
        
        try:
            para_texts = driver.find_elements(By.XPATH, "//div[@class='paragraph-editor grid-layout grid-gap-half'][position() > 1]//span[@data-text='true']")
            time.sleep(2)

            start_index = load_progress(lesson_id)
            if start_index == len(para_texts):
                lesson_links[index] = lesson_link + ",completed\n"
                continue

            for i in range(start_index, len(para_texts)):
                if i > 0 and i % 60 == 0:
                    driver.quit()
                    driver = start_driver()
                    driver.get(lesson_link)
                    login()
                    time.sleep(4)
                    para_texts = driver.find_elements(By.XPATH, "//div[@class='paragraph-editor grid-layout grid-gap-half'][position() > 1]//span[@data-text='true']")
                    time.sleep(4)

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
                                    time.sleep(1)
                                    remove_spacing = driver.find_element(By.XPATH, "(//div[@class='editor-section--item editor-section--controller grid-layout grid-justify--left']//button[@class='has-icon is-white is-rounded button'])[2]")
                                    driver.execute_script("arguments[0].scrollIntoView();", remove_spacing)
                                    time.sleep(1)
                                    driver.execute_script("arguments[0].click();", remove_spacing)
                                    time.sleep(4)
                            except IndexError:
                                break
                    save_progress(i, lesson_id)
                except StaleElementReferenceException:
                    para_texts = driver.find_elements(By.XPATH, "//div[@class='paragraph-editor grid-layout grid-gap-half'][position() > 1]//span[@data-text='true']")
                except NoSuchElementException as e:
                    print(f"An error occurred: {e}")
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
            pass

    with open("lesson_links.txt", "w") as f:
        f.writelines(lesson_links)

lingq_automater()