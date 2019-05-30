import csv

import requests
from bs4 import BeautifulSoup


s = requests.Session()
payload = {
    'email': 'lady.gluh@gmail.com',
    'password': '484334503peps'
}
url = "https://shopme365.com/login/"



followers = s.get('https://www.instagram.com/yuliyamalinka/followers/')






r = s.post(url, data=payload)


file_path = '/home/serg/Desktop/site.csv'


if r.status_code == 200:
    trash_url = 'https://shopme365.com/cart/'
    nr = s.post(trash_url)
    soup = BeautifulSoup(nr.content, 'html.parser')
    table_div = soup.find_all("div",  {'class': 'table-responsive'})[0]
    table = table_div.find_all("table",  {'class': 'table table-bordered'})[0]
    body = table.find("tbody")

    trs = body.find_all('tr')

    with open(file_path, mode='w') as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(['link', 'image_link', 'name', 'weight', 'full_weight', 'count', 'price', 'full_price'])

        for tr in trs:
            tds = tr.find_all('td')
            image_cell = tds[1]
            a = image_cell.find('a')
            page_link = a.attrs['href']
            image_link = a.contents[0].attrs['src']
            product_name = a.contents[0].attrs['title']
            weight = float(str(tds[4].string)[:-2])
            count = float(tds[5].contents[0].contents[1].attrs['value'])
            price = float(tds[6].contents[0].string[1:])
            full_price = price*count
            full_weight = weight*count
            employee_writer.writerow([page_link, image_link, product_name, weight, full_weight, count, price, full_price])
