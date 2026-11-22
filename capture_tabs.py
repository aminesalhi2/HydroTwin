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

# 1. Capture initial overview
driver.save_screenshot('screenshot_overview.png')

# 2. Click '2 Leak' on top segmented control
buttons = driver.find_elements(By.CSS_SELECTOR, '[data-testid="stSegmentedControl"] button')
for b in buttons:
    if '2 Leak' in b.text:
        b.click()
        break
time.sleep(3)
driver.save_screenshot('screenshot_leak_scenario.png')

# 3. Click 'Leak Detection & Work Orders' tab
tabs = driver.find_elements(By.CSS_SELECTOR, '[data-baseweb="tab"]')
for t in tabs:
    if 'Leak Detection' in t.text:
        t.click()
        break
time.sleep(2)
driver.save_screenshot('screenshot_leak_tab.png')

# 4. Click 'Energy Optimization & Outage' tab
tabs = driver.find_elements(By.CSS_SELECTOR, '[data-baseweb="tab"]')
for t in tabs:
    if 'Energy' in t.text:
        t.click()
        break
time.sleep(2)
driver.save_screenshot('screenshot_energy_tab.png')

# 5. Click 'Multilingual Decision Assistant' tab
tabs = driver.find_elements(By.CSS_SELECTOR, '[data-baseweb="tab"]')
for t in tabs:
    if 'Multilingual' in t.text:
        t.click()
        break
time.sleep(2)
driver.save_screenshot('screenshot_assistant_tab.png')

driver.quit()
print('All tab screenshots captured successfully!')
