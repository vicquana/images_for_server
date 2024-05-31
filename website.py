import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_instagram_website_url(username):
    url = f'https://www.instagram.com/{username}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', text=lambda t: t and 'window._sharedData' in t)
        if script_tag:
            shared_data = script_tag.string.partition('=')[-1].strip(' ;')
            data = json.loads(shared_data)
            user_info = data['entry_data']['ProfilePage'][0]['graphql']['user']
            website_url = user_info['external_url']
            return website_url
    return None


def crawl_website(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Example: Extract all links
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links
    return []


def crawl_website_selenium(url):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    
    # Example: Extract all links after page load
    links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a')]
    driver.quit()
    return links


username = 'munoko_cosplay'
website_url = get_instagram_website_url(username)
print('Website URL:', website_url)

if website_url:
    links = crawl_website(website_url)
    print('Links found on the website:', links)
else:
    print('No website found in the Instagram profile.')

if website_url:
    links = crawl_website_selenium(website_url)
    print('Links found on the website:', links)
else:
    print('No website found in the Instagram profile.')
