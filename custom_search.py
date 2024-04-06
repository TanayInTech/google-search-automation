import psycopg2
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data import searches
from createtable import create_table_query

def get_driver():
    driver = webdriver.Chrome()
    return driver

def search_with_custom_date(driver, keyword, start_date, end_date, top_result_count):
    driver.get("https://www.google.com/")
    search = driver.find_element(By.NAME, "q")
    search.send_keys(keyword)
    search.submit()
    
    tools_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "hdtb-tls")))
    tools_btn.click()

    time_dropdown = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "KTBKoe")))
    time_dropdown.click()
    
    custom_range_option = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,"//g-menu[@class='cF4V5c Tlae9d yTik0 PBn44e iQXTJe wplJBd']/g-menu-item[7]//div[@class='YpcDnf OSrXXb HG1dvd']//div[@class='y0fQ9c']//span")))
    custom_range_option.click()
    
    start_date_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "OouJcb")))
    start_date_input.clear()
    start_date_input.send_keys(start_date)
    
    end_date_input = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "rzG2be")))
    end_date_input.clear()
    end_date_input.send_keys(end_date)
    
    go_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//g-button")))
    go_button.click()

    headlines = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3")))
    
    headlines_text = [headline.text for headline in headlines[:top_result_count]]
    return headlines_text

def save_result_in_db(keyword, year, results):
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="9800",
            host="localhost",
            port="5432",
            database="postgres"
        )
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        # Insert search results into the database
        for result in results:
            cursor.execute("INSERT INTO cricket_news (keyword, year, result_text) VALUES (%s, %s, %s)", (keyword, year, result))
        connection.commit()
        print("Records inserted successfully into PostgreSQL table")
        
    except (Exception, psycopg2.Error) as error:
        print("Error while working with PostgreSQL:", error)
        
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

# Main function to process keywords and search results
def process_keywords(searches):
    driver = get_driver()
    
    for search in searches:
        year = search['year']
        keyword = search['keyword']
        top_result_count = search['top_result_count']
        start_date = f"01/01/{year}"
        end_date = f"12/31/{year}"
        
        results = search_with_custom_date(driver, keyword, start_date, end_date, top_result_count)
        save_result_in_db(keyword,year, results)
    
    driver.quit()

# Run the main function with the searches data from data.py
process_keywords(searches)
