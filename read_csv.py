import requests
import time
from bs4 import BeautifulSoup

f = open('output.csv', 'r', encoding='utf-8')

header = "model,production year,motor capacity,power,fuel,km driven,color,state,gearbox,driver hand,price"
keywords = ["Model:", "An de fabricatie:", "Capacitate motor:", "Putere:", "Combustibil:", "Rulaj:", "Culoare:", "Stare:", "Cutie de viteze:", "Volan:"]


def writeToFile(str):
    output = open('data.csv', 'w', encoding='utf-8')
    output.write(str)
    output.close()


def parseValue(value):
    value = value.strip()
    if len(value.split("cm³")) > 1:
        value = value.split("cm³")[0].replace(' ', '')
    elif len(value.split("CP")) > 1:
        value = value.split("CP")[0].replace(' ', '')
    elif len(value.split("km")) > 1:
        value = value.split("km")[0].replace(' ', '')
    elif len(value.split("€")) > 1:
        value = value.split("€")[0].replace(' ', '')
    elif value == "Partea stanga":
        value = 'left-side drive'
    elif value == "Partea dreapta":
        value = 'right-side drive'
    elif value == "Manuala":
        value = 'manual'
    elif value == "Automata":
        value = 'auto'
    elif value == "Utilizat":
        value = 'used'
    elif value == "Nou":
        value = 'new'
    return value


def getDataOlx(page):
    list = page.find_all("li", {"class": "css-1r0si1e"})
    extracted_data = ''

    for keyword in keywords:
        value = "-"

        for element in list:
            data = element.text.split(keyword)
            if len(data) > 1:
                value = parseValue(data[1])
                break

        extracted_data += value + ','

    print(extracted_data)
    return extracted_data


def getDataFromUrl(page_url, price):
    print(page_url)
    data = "-"
    time_interval = 0

    while data.split(',')[0] == "-":
        if time_interval > 1:
            return ''
        time.sleep(time_interval)
        time_interval += 1  # cooldown to add in case your request got blocked
        response = requests.get(page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        data = getDataOlx(soup)

    return '\n' + data + parseValue(price)


def startScript():
    global header
    for line in f:
        line = line.split(',')
        url = line[-1].strip()
        price = line[1].strip()
        if url[0] != 'h':
            continue
        if len(url.split('autovit.ro')) > 1:
            continue

        header += getDataFromUrl(url, price)
        writeToFile(header)

