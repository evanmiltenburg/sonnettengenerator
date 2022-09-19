import requests
import time
import json
from bs4 import BeautifulSoup

################################################################################
# General utils 

def get_texts(elem):
    "Get texts from an element, separated by line breaks."
    texts = []
    for e in elem.descendants:
        if isinstance(e, str):
            texts.append(e.strip())
    return texts

################################################################################
# Separate functions to extract data from a row in the table

def get_title(row):
    "Get title from a row"
    return row.find('span', attrs={'class':'trunk'}).text

def get_download_links(row):
    "Get download links from a row."
    result = dict()
    for link in row.find_all('a'):
        if 'download' in link.attrs:
            url = link['href']
            extension = url.split('.')[-1]
            result[extension] = 'https://www.dbnl.org' + url
    return result

################################################################################
# Main functions

def extract_metadata(row):
    cells = row.find_all('td')
    return dict(id=row['id'],
                title=get_title(row),
                download=get_download_links(row),
                edition=cells[1].text,
                year=cells[2].text,
                auteur=cells[3].text,
                genres=get_texts(cells[4]))

def extend_metadata(content, metadata):
    "Extract metadata from page and add it to the metadata list."
    soup = BeautifulSoup(content, features="lxml")
    table = soup.find_all('tr')
    table_body = table[1:]
    for row in table_body:
        entry = extract_metadata(row)
        metadata.append(entry)

metadata = []
for page in range(1,59):
    url = f'https://www.dbnl.org/titels/titels_ebook.php?s=t&p={page}'
    print(url)                              # show current page.
    content = requests.get(url).content     # download content.
    extend_metadata(content, metadata)      # extract info.
    time.sleep(2)                           # Be nice to dbnl, wait 2 seconds!

with open('resources/dbnl.json', 'w') as f:
    json.dump(metadata, f, indent=2)
