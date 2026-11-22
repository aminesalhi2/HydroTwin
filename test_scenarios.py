from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

opt = Options()
opt.add_argument('--headless=new')
opt.add_argument('--window-size=1440,960')
driver = webdriver.Chrome(options=opt)
driver.get('http://localhost:8501')
time.sleep(3)

# Click '2 Leak' button
try:
    leak_btn = driver.find_element(By.XPATH, "//button[contains(., '2 Leak')]")
    leak_btn.click()
    time.sleep(3)
    driver.save_screenshot('screenshot_2_leak_active.png')
    
    # Also switch to leak tab
    tabs = driver.find_elements(By.CSS_SELECTOR, '[data-baseweb="tab"]')
    for t in tabs:
        if 'Leak' in t.text:
            t.click()
            break
    time.sleep(2)
    driver.save_screenshot('screenshot_2_leak_ticket.png')
except Exception as e:
    print('Error on 2 Leak:', e)

# Click '4 Power cut' button
try:
    outage_btn = driver.find_element(By.XPATH, "//button[contains(., '4 Power cut')]")
    outage_btn.click()
    time.sleep(3)
    driver.save_screenshot('screenshot_4_outage_active.png')
except Exception as e:
    print('Error on 4 Power cut:', e)

driver.quit()
print('Scenarios tested!')
