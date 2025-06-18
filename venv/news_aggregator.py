import requests
import csv

from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Method to check for invalid URLs before trying to scrape
def request_catching(url, headers):
    try:
        request = requests.get(url, headers=headers, timeout=10)
        if request.status_code == 404:
            print(f'\n❌ No website found for: {url}\n')
            exit()
        elif request.status_code != 200:
            print(f'\n⚠️  Failed to load website (status code {request.status_code}). Try again later.\n')
            exit()
    except requests.exceptions.MissingSchema:
        print('\n❌ Your news outlet link is incorrect. Please double check it and retry.\n')
        exit()
    except requests.exceptions.RequestException as e:
        print(f'\n❌ A network error occurred: {e}\n')
        exit()
    return request

# Assigning URLs for each site we are scraping
# Can change these or update as time goes on
npr_url = 'https://www.npr.org/sections/news/'
techcrunch_url = 'https://techcrunch.com/latest/'
hackernews_url = 'https://news.ycombinator.com/best'
bbc_url = 'https://www.bbc.com/news/world'

# Headers to look friendly to website
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Request each URL for each site
npr_request = request_catching(npr_url, headers)
techcrunch_request = request_catching(techcrunch_url, headers)
hackernews_request = request_catching(hackernews_url, headers)
bbc_request = request_catching(bbc_url, headers)

# Parsing the HTML from each webpage
npr_soup = BeautifulSoup(npr_request.text, 'html.parser')
techcrunch_soup = BeautifulSoup(techcrunch_request.text, 'html.parser')
hackernews_soup = BeautifulSoup(hackernews_request.text, 'html.parser')
bbc_soup = BeautifulSoup(bbc_request.text, 'html.parser')

# Writing to file with headline and teaser for each news website
npr_file = open('npr.csv', mode='w', newline='', encoding='utf-8')
npr_writer = csv.writer(npr_file)
npr_writer.writerow(['Headline', 'Teaser'])

techcrunch_file = open('techcrunch.csv', mode='w', newline='', encoding='utf-8')
techcrunch_writer = csv.writer(techcrunch_file)
techcrunch_writer.writerow(['Headline', 'Teaser'])

hackernews_file = open('hackernews.csv', mode='w', newline='', encoding='utf-8')
hackernews_writer = csv.writer(hackernews_file)
hackernews_writer.writerow(['Headline'])

bbc_file = open('bbc.csv', mode='w', newline='', encoding='utf-8')
bbc_writer = csv.writer(bbc_file)
bbc_writer.writerow(['Headline', 'Summary'])

# Blocks of HTML for all soups
npr_block = npr_soup.find_all('div', class_='item-info-wrap')
techcrunch_block = techcrunch_soup.find_all('div', class_='wp-block-techcrunch-card wp-block-null')
hackernews_block = hackernews_soup.find_all('tr', class_='athing submission')
bbc_block = bbc_soup.find_all('div', class_='sc-225578b-0 btdqbl')

# Looping through each block and extracting information
try:
    for i in npr_block:

        # Getting the headline and teaser from html
        headline = i.find('h2', class_='title').get_text()
        npr_teaser = i.find('p', class_='teaser').get_text()

        # Removing date from teaser
        date = i.find('span', class_='date').get_text()
        npr_teaser = npr_teaser.replace(date, '')

        # Writing headline and teaser to CSV
        npr_writer.writerow([headline, npr_teaser])
    print('\n✅ NPR: Found the latest NPR headlines and teasers.')
except Exception as e:
    print(f'\n⚠️  NPR scraping failed: {e}')

# Creates a teaser with summary section
try:
    for i in techcrunch_block:

        # Get headline
        headline_tag = i.find('h3', class_='loop-card__title').find('a')
        headline = headline_tag.get_text() if headline_tag else 'N/A'

        # Get href and scrape teaser from next page
        href = i.find('a', class_='loop-card__title-link')['href']
        href_request = requests.get(href, headers=headers)
        techcrunch_next_request = BeautifulSoup(href_request.text, 'html.parser')
        techcrunch_teaser_tag = techcrunch_next_request.find('p', id='speakable-summary')
        techcrunch_teaser = techcrunch_teaser_tag.get_text() if techcrunch_teaser_tag else 'N/A'

        # Write headline and teaser to CSV
        techcrunch_writer.writerow([headline, techcrunch_teaser])
    print('✅ TechCrunch: Found the latest TechCrunch headlines and teasers.')
except Exception as e:
    print(f'⚠️  TechCrunch scraping failed: {e}')

# No teaser because top stories are often linked to various different news outlet pages
try:
    for i in hackernews_block:

        # Get headline
        headline = i.find('span', class_='titleline').get_text()

        # Write headline to CSV
        hackernews_writer.writerow([headline])
    print('✅ Hacker News: Found the latest Hacker News headlines.')
except Exception as e:
    print(f'⚠️  Hacker News scraping failed: {e}')

# Creates a summary since information is in paragraph form
try:
    for i in bbc_block:

        # Initialize summary
        bbc_summary = ''

        # Get headline
        headline = i.find('div', class_='sc-9d830f2a-0 eKWlJZ').get_text()

        # Get href and scrape teaser from next page
        href = i.find('a', class_='sc-8a623a54-0 hMvGwj')['href']
        href_request = requests.get(urljoin(bbc_url, href), headers=headers)
        bbc_next_request = BeautifulSoup(href_request.text, 'html.parser')
        bbc_summary_block = bbc_next_request.find_all('p', class_='sc-9a00e533-0 hxuGS')

        # Goes through all paragraphs and makes a summary
        for j in bbc_summary_block:
            bbc_summary_section = j.get_text()
            bbc_summary = bbc_summary + bbc_summary_section

        # Write headline and summary to CSV
        bbc_writer.writerow([headline, bbc_summary])
    print('✅ BBC: Found the latest BBC headlines and summaries.\n')
except Exception as e:
    print(f'⚠️  BBC scraping failed: {e}\n')

# Safely closing CSV files
npr_file.close()
techcrunch_file.close()
hackernews_file.close()
bbc_file.close()
