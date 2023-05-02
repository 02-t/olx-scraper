from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import multiprocessing
multiprocessing.set_start_method('spawn', True)


class MyDict(dict):
    @property
    def text(self):
        return self['text']


def findElement(parent, child, attribute=None, value=None, wait=False):
    str = child
    a = None

    if attribute:
        str = child + "[" + attribute + "='" + value + "']"

    try:
        if wait:
            WebDriverWait(parent, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, str)))
        a = parent.find_element(By.CSS_SELECTOR, str)
    except:
        a = MyDict({'text': "NOT SPECIFIED"})

    return a


def findElements(parent, child, attribute=None, value=None, wait=False):
    str = child

    if attribute:
        str = child + "[" + attribute + "='" + value + "']"

    if wait:
        WebDriverWait(parent, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, str)))

    return parent.find_elements(By.CSS_SELECTOR, str)


def writeToFile(str):
    f = open('output.csv', 'w', encoding='utf-8')
    f.write(str)
    f.close()


def getProducts(new_driver):
    return findElements(new_driver, 'div', 'class', 'css-qfzx1y')


def getValuesFromProducts(product):
    name = findElement(product, 'h6').text.replace(',', ' - ').replace(';', ' - ')
    print(name)
    price = findElement(product, 'p', 'data-testid', 'ad-price').text.replace('\n', '').replace(',', '.')
    location_date = findElement(product, 'p', 'data-testid', 'location-date').text.replace(',', ' - ')
    km = findElement(product, 'div', 'class', 'css-efx9z5').text.replace(',', ' - ')
    state = findElement(product, 'span', 'class', 'css-3lkihg').text.replace(',', ' - ')

    return name, price, location_date, km, state


def scanForProducts(products_count, data, new_url, new_driver, new_wait):
    page = 1
    product_nr = 0

    while page <= 25:
        time.sleep(5)
        for product in getProducts(new_driver):
            if products_count <= product_nr:
                return data
            name, price, location_date, km, state = getValuesFromProducts(product)
            data += name + ',' + price + ',' + location_date + ',' + km + ',' + state + '\n'
            product_nr += 1

        if products_count <= product_nr:
            break

        page += 1
        new_driver.get(new_url+"/?page=" + str(page))
        new_wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    return data


def getProductsCount(new_driver):
    products_count = findElement(new_driver, 'div', 'data-testid', 'total-count').text.split(' ')[2]
    if products_count == 'peste':
        products_count = 1000

    return int(products_count)


def get_data(halved_city_list):
    print('halved data', halved_city_list)
    new_driver = webdriver.Firefox()
    new_wait = WebDriverWait(new_driver, 10)
    new_wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    data = ""

    for city in halved_city_list:
        new_url = 'https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/' + city.replace(' ', '-').lower()
        new_driver.get(new_url)
        products_count = getProductsCount(new_driver)
        print(city, "are", products_count, "produse")

        data = scanForProducts(products_count, data, new_url, new_driver, new_wait)

    return data


if __name__ == '__main__':
    header = 'name,price,location_date,km,state\n'
    url = 'https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme'

    driver = webdriver.Firefox()
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    findElement(driver, 'button', 'id', 'onetrust-accept-btn-handler', True).click()
    time.sleep(1)

    findElement(driver, 'input', 'class', 'css-uvldze', True).click()

    region_max = len(findElements(driver, 'li', 'data-cy', 'regions-item', True))
    #city_list = []
    city_list = ["Braila", "Brasov", "Focsani", "Bucuresti"]


    """
    for region_count in range(0, region_max):
        region = findElements(driver, 'li', 'data-cy', 'regions-item', True)[region_count]
        region.click()
        cities = findElements(driver, 'li', 'data-cy', 'city-item', True)

        for city in cities:
            city_list.append(city.text)

        findElement(driver, 'button', 'data-cy', 'cities-back-button').click()
    """

    city_count = len(city_list)
    n = city_count // 4  # number of elements in each subarray
    remainder = city_count % 4  # remainder elements if any

    city_lists = []
    start = 0
    for i in range(4):
        if i < remainder:
            end = start + n + 1
        else:
            end = start + n
        subarray = city_list[start:end]
        city_lists.append(subarray)
        start = end

    driver.quit()

    print("Sunt", city_count, "orase gasite, timp estimat de finisare", city_count*2.5/60/60, 'ore')

    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(get_data, [city_lists[0], city_lists[1], city_lists[2], city_lists[3]])

    print("\n\n\n\n\nSCRIPT ENDED - olx web scraper by 02-t\n\n\n\n\n")

    header += results[0] + results[1] + results[2] + results[3]

    writeToFile(header)
