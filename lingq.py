from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium import webdriver
import os
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import csv

load_dotenv()
USERNAME = os.getenv('LINGQ_USERNAME')
PASSWORD = os.getenv('LINGQ_PASSWORD')


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
options.add_argument('--headless=new')


def start_driver():
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

driver = start_driver()

def extract_lesson_id(lesson_link):
    return lesson_link.split('/')[-1].strip()

def save_progress(lesson_id, last_removed_index):
    with open(f"{lesson_id}_progress.txt", "w") as f:
        f.write(str(last_removed_index))

def load_progress(lesson_id):
    file_name = f"{lesson_id}_progress.txt"
    if not os.path.exists(file_name):
        return None
    with open(file_name, "r") as f:
        return int(f.read().strip())

def modal_close():
    try:
        iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//iframe[@id='wiz-iframe-intent']")))
        if iframe:
            print('Found iframe')
        driver.switch_to.frame(iframe)
        
        close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='CT_InterstitialClose']")))
        if close_button:
            print('Found modal close button')
        close_button.click()
        
        driver.switch_to.default_content()
    except NoSuchElementException:
        print('Could not find modal close button')
    except Exception as e:
        print(f"An error occurred while closing modal: {e}")
        pass

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
    with open('info2.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  
        lesson_links = []
        remove_indexes = []
        
        for row in reader:
            lesson_links.append(row[-1])
            remove_indexes.append(row[2])
    
    remove_indexes = [list(map(int, index.split('/'))) for index in remove_indexes]
    
    for lesson_link in lesson_links:
        lesson_id = extract_lesson_id(lesson_link)
        last_removed_index = load_progress(lesson_id)
        
        print("Lesson link", lesson_link)
        driver.get(lesson_link)
        time.sleep(3)
        
        if "login" in driver.current_url:
            login()
        time.sleep(3)
        
        if last_removed_index is not None:
            try:
                start_index = remove_indexes[lesson_links.index(lesson_link)].index(last_removed_index) + 1
            except ValueError:
                start_index = 0
        else:
            start_index = 0
        
        for remove_index in remove_indexes[lesson_links.index(lesson_link)][start_index:]:
            try:
                print("Removing index", remove_index)
                para_text = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"(//div[@class='paragraph-editor grid-layout grid-gap-half'][position() > 1]//span[@data-text='true'])[{remove_index}]")))
                driver.execute_script("arguments[0].scrollIntoView();", para_text)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", para_text)
                time.sleep(1)
                remove_spacing = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[.='Absatzabstand löschen']")))
                driver.execute_script("arguments[0].scrollIntoView();", remove_spacing)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", remove_spacing)
                save_progress(lesson_id, remove_index)
                time.sleep(4)
                

            except Exception as e:
                print(f"didnt removed index {remove_index}")
                continue

lingq_automater()
