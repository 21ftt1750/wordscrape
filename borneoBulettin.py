import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pandas as pd

categories = {
        "national": "1",
        "sea": "2",
        "world": "3",
        "business": "4",
        "technology": "5",
        "lifestyle": "6",
        "entertainment": "7",
        "sports": "8",
        "features": "9"
    }

def init_driver():
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    return driver

def close_ads(driver):
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tdm-pmh-close"))
    ).click()
    return driver
def change_categories(value, driver):
    category_xpath = f"//*[@id=\"menu-news-category-2\"]/li[{value}]/a"
    category_element = driver.find_element(By.XPATH, category_xpath)
    category_element.click()
    return driver

def module_block_finder(driver):
    WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "td-module-meta-info"))
        )
    return driver

def get_articles_data(driver, processed_urls, category):
    current_date = datetime.now().date()
    titles = []
    links = []
    times_today = []
    times_posted = []        
    articles = driver.find_elements(By.CLASS_NAME, "td-module-meta-info")        
    for article in articles:
        title = article.find_element(By.TAG_NAME, 'h3').text
        link = article.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, "a").get_attribute("href")
        time_element = article.find_element(By.TAG_NAME, 'time')
        datetime_value = time_element.get_attribute("datetime")[:10]           
        if str(datetime_value) == str(current_date) and link not in processed_urls:  
            titles.append(title)
            links.append(link)
            times_today.append(current_date)
            times_posted.append(datetime_value)
            processed_urls.add(link)       
    category_data = {
        'Category': category,
        'Link': links,
        'Article': titles,
        'Date': times_posted
    }      
    return category_data  

def scrape_and_save_news():
    driver = init_driver()
    driver.get("https://borneobulletin.com.bn/")
    driver = close_ads(driver) 
    all_data = []
    processed_urls = set()      
    for category, value in categories.items():
        driver = change_categories(value, driver)
        driver = module_block_finder(driver)       
        category_data = get_articles_data(driver, processed_urls, category)
        all_data.append(category_data) 
    driver.quit()
    combined_data = pd.concat([pd.DataFrame(data) for data in all_data])
    combined_data.to_csv('borneo_bulletin.csv', index=False)
    print("All data saved to 'borneo_bulletin.csv'")
if __name__ == '__main__':
    scrape_and_save_news()