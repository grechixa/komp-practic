from bs4 import BeautifulSoup
import requests
import csv

base_url = "https://atlas.herzen.spb.ru/teachers?page="

def get_person(url):
    response = requests.get(url)
    response.raise_for_status()

    my_soup = BeautifulSoup(response.text, 'html.parser')

    cells = my_soup.find_all('tr')

    results = []
    for cell in cells:
        if cell.a:
            name = cell.a.text.strip()
            profile_url = "https://atlas.herzen.spb.ru" + cell.a['href']
            item = {
                "name": name,
                "url": profile_url
            }
            results.append(item)
    return results

def get_person_details(profile_url):
    pass


data = []
for i in range(1,55):
    page_url = base_url + str(i)
    data.extend(get_person(page_url))

fieldnames = ["name", "url", "email", "phone"]
with open('file.csv', mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(data)
