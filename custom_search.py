import psycopg2
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data import searches
from createtable import create_table_query
import time
from selenium.webdriver.common.keys import Keys

def get_driver():
    driver = webdriver.Chrome()
    return driver


def search_with_custom_date(driver, keyword, start_date, end_date, top_result_count):
    driver.get("https://www.google.com/")
    search = driver.find_element(By.NAME, "q")
    search.send_keys(keyword)
    search.submit()
    timer = 30
    tools_btn = WebDriverWait(driver, timer).until(EC.element_to_be_clickable((By.ID, "hdtb-tls")))
    tools_btn.click()

    time_dropdown = WebDriverWait(driver, timer).until(EC.element_to_be_clickable((By.CLASS_NAME, "KTBKoe")))
    time_dropdown.click()

    custom_range_option = WebDriverWait(driver, timer).until(EC.element_to_be_clickable((By.XPATH,
                                                                                         "//g-menu[@class='cF4V5c Tlae9d yTik0 PBn44e iQXTJe wplJBd']/g-menu-item[7]//div[@class='YpcDnf OSrXXb HG1dvd']//div[@class='y0fQ9c']//span")))
    custom_range_option.click()

    start_date_input = WebDriverWait(driver, timer).until(EC.element_to_be_clickable((By.ID, "OouJcb")))
    start_date_input.clear()
    start_date_input.send_keys(start_date)

    end_date_input = WebDriverWait(driver, timer).until(EC.element_to_be_clickable((By.ID, "rzG2be")))
    end_date_input.clear()
    end_date_input.send_keys(end_date)

    go_button = WebDriverWait(driver, timer).until(EC.element_to_be_clickable((By.XPATH, "//g-button")))
    go_button.click()

    unique_headlines = set()

    while len(unique_headlines) < top_result_count:

        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)

        headlines_on_page = WebDriverWait(driver, timer).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3")))
        new_headlines = {headline.text for headline in headlines_on_page}
        unique_headlines.update(new_headlines)

        if len(new_headlines) == 0:
            break

    return list(unique_headlines)[:top_result_count]


def save_result_in_db(keyword, year, results):
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="9800",
            host="localhost",
            port="5432",
            database="postgres",
            client_encoding="utf-8"
        )
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        # Insert search results into the database
        for result in results:
            cursor.execute("INSERT INTO IPLnews1 (keyword, year, result_text) VALUES (%s, %s, %s)",
                           (keyword, year, result))
        connection.commit()
        print("Records inserted successfully into PostgreSQL table")

        today = datetime.now().date().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT * FROM IPLnews1 WHERE date_trunc('day', execution_time) = %s", (today,))
        records = cursor.fetchall()

        # Print the fetched data
        print("Today's Inserted Data:")
        for record in records:
            print("ID:", record[0])
            print("Keyword:", record[1])
            print("Year:", record[2])
            print("Result Text:", record[3])
            print("Timestamp:", record[4])
            print()

            file_name = datetime.today().strftime("%Y-%m-%d %H %M %S")
            with open(file_name + ".csv", 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['ID', 'keyword', 'year', 'result_text', 'Timestamp'])
                csv_writer.writerows(records)
                print("Records Saved as a CSV file")

    except (Exception, psycopg2.Error) as error:
        print("Error while working with PostgreSQL:", error)
        

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def process_keywords(searches):
    driver = get_driver()

    try:
        for search in searches:
            year = search['year']
            keyword = search['keyword']
            top_result_count = search['top_result_count']
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)

            # Convert datetime objects to string format
            start_date_str = start_date.strftime("%m/%d/%y")
            end_date_str = end_date.strftime("%m/%d/%Y")

            results = search_with_custom_date(driver, keyword, start_date_str, end_date_str, top_result_count)
            save_result_in_db(keyword, year, results)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()


# Run the main function with the searches data from data.py
process_keywords(searches)
