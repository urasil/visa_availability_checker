from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException  
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from plyer import notification

CHECK_INTERVAL = 5  # Check every 5 minutes

def print_all_elements_under_element(element):
    try:
        elements = element.find_elements(By.XPATH, ".//*")
        for e in elements:
            print(e.tag_name)

    except Exception as e:
        print(f"Error: {e}")

class FormSolver:
    def __init__(self):
        self.url = 'https://basvuru.kosmosvize.com.tr/appointmentform' 
        self.tc = os.getenv('TC')

    def setup_driver(self):
        options = Options()
        #options.add_argument('--headless')  # headless mode
        options.add_argument('--disable-gpu')
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        self.driver = driver
        return driver

    def click_sonraki(self):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sonraki')]")))

            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.driver.execute_script("arguments[0].removeAttribute('disabled')", button)
            self.driver.execute_script("arguments[0].click();", button)
            print("Clicked 'Sonraki' button")

        except Exception as e:
            print(f"An error occurred: {e}")


    def select_city(self):
        self.driver.get(self.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "cities"))
        )
        city_dropdown = Select(self.driver.find_element(By.ID, "cities"))
        city_dropdown.select_by_visible_text("Istanbul")  

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sp-selectable-button"))
        )
        istanbul_button = self.driver.find_element(By.XPATH, "//div[@class='sp-selectable-button' and contains(text(), 'İstanbul')]")
        istanbul_button.click()
        self.click_sonraki()

    @DeprecationWarning
    #not working
    def click_recaptcha(self):
        try:
            recaptcha_iframe = WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='reCAPTCHA']"))
            )

            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-checkmark"))
            )
            checkbox.click()
            print("reCAPTCHA checkbox clicked")

            self.driver.switch_to.default_content()

        except Exception as e:
            print(f"An error occurred: {e}")

    def alert_user(self):
        notification.notify(
            title="Attention Required",
            message="Please solve the reCAPTCHA manually.",
            timeout=10 
        )
        os.system('echo \a')

    def fill_form(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "__BVID__123"))
            )
            select_element_123 = Select(self.driver.find_element(By.ID, "__BVID__123").find_element(By.TAG_NAME, "select"))
            select_element_123.select_by_value("1")
            print("Option selected for __BVID__85")

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "__BVID__130"))
            )
            
            select_element_92 = Select(self.driver.find_element(By.ID, "__BVID__130").find_element(By.TAG_NAME, "select"))
            select_element_92.select_by_value("16")
            
            print("Option selected for __BVID__130")

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "__BVID__127"))
            )
            
            input_element_89 = self.driver.find_element(By.ID, "__BVID__127").find_element(By.TAG_NAME, "input")
            self.driver.execute_script("arguments[0].removeAttribute('disabled')", input_element_89)
            input_element_89.clear()
            input_element_89.send_keys(self.tc)
            print("Number entered for __BVID__127")

            while True:
                self.alert_user()
                if input("Have you solved the reCAPTCHA? (y/n): ") == 'y':
                    time.sleep(1)
                    break
            time.sleep(5)
            self.click_sonraki()
            time.sleep(7)

            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(1)
        
        except TimeoutException:
            print("Timed out waiting for element to be present.")

        except NoSuchElementException as e:
            print(f"Element not found: {e}")

        except Exception as e:
            print(f"Error: {e}")


class AppointmentChecker:
    def __init__(self, driver):
        self.driver = driver
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.toemail = os.getenv('TOEMAIL')

    def check_appointments(self):
        time.sleep(10)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "vdp-datepicker__calendar"))
            )

            count = 10
            while count > 0:
                calendar = self.driver.find_element(By.CLASS_NAME, "vdp-datepicker__calendar")
                days = calendar.find_elements(By.CLASS_NAME, "cell")
                next_button = self.driver.find_element(By.CSS_SELECTOR, ".vdp-datepicker__calendar header .next")
                prev_button = self.driver.find_element(By.CSS_SELECTOR, ".vdp-datepicker__calendar header .prev")
                
                for day in days:
                    print(day.text)
                    day_avail = day.get_attribute("class")
                    if "disabled" not in day_avail and "blank" not in day_avail and "header" not in day_avail:
                        date = day.text
                        self.notify_user(date)
                        print("date found: ", day.text)
                        return True
                
                is_next_disabled = "disabled" in next_button.get_attribute("class")
                print("is_next_disabled: ", is_next_disabled)
                if is_next_disabled:
                    is_prev_disabled = "disabled" in prev_button.get_attribute("class")
                    while not is_prev_disabled:
                        prev_button.click()
                        time.sleep(2)
                        is_prev_disabled = "disabled" in prev_button.get_attribute("class")
                next_button.click()
                print("Clicked next button")
                time.sleep(2) 
                count -= 1
                
        except Exception as e:
            print(f"Error: {e}")
        
        return False

    def notify_user(self, date):
        subject = 'Visa Appointment Available'
        body = f'An appointment is available on {date}. Check it here: {self.url}'
        
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.toemail
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.email, self.password)
        text = msg.as_string()
        server.sendmail(self.email, self.toemail, text)
        server.quit()

        print(f'Notification sent for appointment on {date}.')

    def job(self):
        print('Checking for appointments...')
        found = self.check_appointments()
        if not found:
            print('No available appointments found. Rechecking in 5 minutes.')

def main():
    try:
        form_solver = FormSolver()
        driver = form_solver.setup_driver()
        form_solver.select_city()
        form_solver.fill_form()

        appointment_checker = AppointmentChecker(driver)
        while True:
            appointment_checker.job()
            time.sleep(CHECK_INTERVAL * 60)  # Check every 5 minutes
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
    print("Program ended.")