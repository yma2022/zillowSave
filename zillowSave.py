import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import time
import urllib.parse
from bs4 import BeautifulSoup

# Function to sanitize the directory name
def sanitize_title(title):
    illegal_chars = '<>:"/\\|?*'
    return ''.join(c for c in title if c not in illegal_chars)

def zillowSave(url):
    options = Options()
    options.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }


    driver = webdriver.Chrome(options=options)

    try:
        # Load the page
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-cy="gallery-see-all-photos-button"]')))
        button.click()

        time.sleep(random.randint(5,10))

        scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[class^="DialogBody-"]')
        scroll_increment = 400
        attempt_count = 0  
        max_attempts = 100 

        while attempt_count < max_attempts:
            # Scroll the specific element
            driver.execute_script("arguments[0].scrollTop += arguments[1]", scrollable_div, scroll_increment)
            time.sleep(4) 
            attempt_count += 1

        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li')))

        page_source = driver.page_source  
        soup = BeautifulSoup(page_source, 'html.parser')
        li_elements = soup.find_all('li')

        li_extracted = [
            li_element for li_element in li_elements
            if li_element.get('class') and any(cls.startswith('Tile__StyledTile') for cls in li_element.get('class'))
        ]

        print(f"Total <li> elements found: {len(li_extracted)}")

        title = driver.title.strip() if driver.title else "default_title"
        title_safe = sanitize_title(title)

        # Create the directory to save images
        save_dir = os.path.join('.', 'images', title_safe)
        os.makedirs(save_dir, exist_ok=True)

        picture_list = []
        for ele in li_extracted:
            if ele.find('picture'):
                picture_list.append(ele.find('picture'))
        print(f"Total <picture> elements found: {len(picture_list)}")
        img_list = [element.find('img') for element in picture_list]
        print(f"Total <img> elements found: {len(img_list)}")
        for li_element in li_extracted:
            picture_element = li_element.find('picture')
        
            if picture_element:           
                img_tag = picture_element.find('img')
                
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    
                    parsed_url = urllib.parse.urlparse(img_url)
                    filename = os.path.basename(parsed_url.path)
                    idx = 0
                    if not filename:
                        filename = f'image_{idx}.jpg'
                        idx += 1
                    save_path = os.path.join(save_dir, filename)
                    # Download the image
                    try:
                        img_response = requests.get(img_url)
                        if img_response.status_code == 200:
                            with open(save_path, 'wb') as f:
                                f.write(img_response.content)
                            print(f"Downloaded {img_url} to {save_path}")
                        else:
                            print(f"Failed to download {img_url} (Status code: {img_response.status_code})")
                        time.sleep(random.randint(20,40))
                    except Exception as e:
                        print(f"Error downloading {img_url}: {e}")
            else:
                print("No picture found!")
    finally:
        driver.quit()

if __name__=="__main__":
    print("Please input the zillow house detail page link:")
    url = input()
    zillowSave(url)
