from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import csv
import requests
from datetime import datetime

#d290e592-2552-4a00-a705-3102caecc473

def price_history(a): # function for price history
    url = a

    params = {
        "start_date": "all",
        "end_date": "2021-08-19",
        "intervals": "100", # change intervals here
        "format": "highstock",
        "currency": "USD",
        "country": "US"
    }

    headers = {
        "accept-encoding": "gzip, deflate",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    for timestamp, price in response.json()["series"][0]["data"]:
        date = datetime.utcfromtimestamp(int(timestamp) // 1000)
        yield date, price


def Sales_History(sku): #function for sales history
    url = f"https://stockx.com/api/rest/v2/products/{sku}/activity?state=480&currency=USD&limit=250&page=1&sort=createdAt&order=DESC"
    
    headers = {
        "accept-encoding": "gzip, deflate",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    response = requests.get(url, headers=headers)
    
    #files = response.json()

    table = response.json()["ProductActivity"]

    for sale in table:
        yield sale['createdAt'][:10], sale['createdAt'][11:19], sale['localAmount']


file_save_path = "/Users/lavasrani/Documents/web_scrapping/"

path = "/Users/lavasrani/Documents/web_scrapping/chromedriver"
option = Options()
option.headless = False
driver = webdriver.Chrome(path,options=option)
driver.get("https://stockx.com/retro-jordans") # -----------Paste the link here-----------------

close = driver.find_element_by_css_selector("button.chakra-button.css-zysaad")
print(close)
print(close.text)
close.click()

file = open("Shoes_Description.csv","w")
written = csv.writer(file)

for page in range(1,5): # change it to the number of pages (last page+1)
    current = driver.current_url
    current = current[18:]
    print(current)
    for iterate in range(1,41):
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"div.tile.browse-tile:nth-of-type({iterate})"))
        )
        try:
            link = WebDriverWait(element, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "price-line-div"))
            )
            link.click()

        except:
            print("Fail 2")
        try:
            product_name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.name"))
            )
            product = [product_name.text]

            ticker = driver.find_element_by_css_selector("span.soft-black")
            product.append(ticker.text)

            product_details= [i.text for i in driver.find_elements_by_css_selector(".detail>span")]
            product += product_details
            print(product)

            current_shoe = driver.current_url
            product.append(current_shoe)

            if iterate == 1:
                written.writerow(['Product Name','Ticker','Style','Colorway','Retail Price','Release Date','URL'])
            written.writerow(product)

            url_search = driver.find_element_by_css_selector("div.product-view>script[type='application/ld+json']")
            json_data = url_search.get_attribute('innerHTML')

            model = json.loads(json_data)  

            url_ = f"https://stockx.com/api/products/{model['sku']}/chart"
            file_name = str(product_name.text)
            print(type(file_name)) 
            file_name = file_name.replace(" \'",' ').replace('/',' ')
            print(file_name)
            with open(f"{file_name}.csv","w") as f:
                writer = csv.writer(f)
                writer.writerow(['date','price'])
                for date,price in price_history(url_):
                    data = [date,price]
                    writer.writerow(data)
            with open(f"sales_history_{file_name}.csv","w") as f:
                writer = csv.writer(f)
                writer.writerow(['Date','Time','Price'])
                for date,tim,price in Sales_History(model['sku']):
                    data = [date,tim,price]
                    writer.writerow(data)

        except:
            product_name = driver.find_element_by_css_selector("h1.chakra-heading.primary-product-title.css-1gbu8yz")
            product_name1 = driver.find_element_by_css_selector("h1.chakra-heading.secondary-product-title.css-10v5fk5")
            product = [product_name.text + ' ' + product_name1.text]

            driver.execute_script("window.scrollTo(0,550);")

            time.sleep(3)

            product_details= [i.text for i in driver.find_elements_by_css_selector("p.chakra-text.css-xxhgqu")]
            product += product_details

            driver.execute_script("window.scrollTo(0,1050);")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "dd.chakra-stat__number.css-wljxya"))
            )

            product_details= [i.text for i in driver.find_elements_by_css_selector("dd.chakra-stat__number.css-wljxya")]
            print(product_details)
            product.append(product_details[3])
            product.append(product_details[5])

            current_shoe = driver.current_url
            product.append(current_shoe)

            print(product)

            if iterate == 1:
                written.writerow(['Product Name','Style','Colorway','Retail Price','Release Date','Number of sales','avg price','URL'])
            written.writerow(product)

            url_search = driver.find_element_by_css_selector("div.chakra-container.new-product-view.css-vp2g1e>script")
            json_data = url_search.get_attribute('innerHTML')

            model = json.loads(json_data)

            url_ = f"https://stockx.com/api/products/{model['sku']}/chart"
            file_name = str(product_name.text + ' ' + product_name1.text)
            print(type(file_name)) 
            file_name = file_name.replace(" \'",' ').replace('/',' ')
            print(file_name)
            with open(f"{file_name}.csv","w") as f:
                writer = csv.writer(f)
                writer.writerow(['date','price'])
                for date,price in price_history(url_):
                    data = [date,price]
                    writer.writerow(data)

            with open(f"sales_history_{file_name}.csv","w") as f:
                writer = csv.writer(f)
                writer.writerow(['Date','Time','Price'])
                for date,tim,price in Sales_History(model['sku']):
                    data = [date,tim,price]
                    writer.writerow(data)

        driver.back()
    time.sleep(3)

    next = driver.find_element_by_css_selector(f"a[href='{current}?page={page+1}']>svg.chakra-icon.css-2evpa9")
    next.click()

file.close()


    


    



