import os
import re
import requests
import time
from bs4 import BeautifulSoup
from blacklist import BLACKLISTED_CLASSES, BLACKLISTED_IDS

def download_4chan_thread(thread_url, base_dir='threads', progress_callback=None, cancel_check=None):
    # 4chan demands for requests to have a user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # getting url of the thread
    match = re.search(r'boards\.4chan\.org/([^/]+)/thread/(\d+)', thread_url)
    if not match:
        print('URL is invalid')
        return
    
    board = match.group(1)
    thread_id = match.group(2)
    
    # creating dirs
    thread_dir = os.path.join(base_dir, f'{board}_{thread_id}')
    images_dir = os.path.join(thread_dir, 'images')
    thumbs_dir = os.path.join(thread_dir, 'thumbs')
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(thumbs_dir, exist_ok=True)
    
    print(f'Downloading thread /{board}/{thread_id}...')
    
    # getting html
    response = requests.get(thread_url, headers=headers)
    html = response.text
    
    # gettings all links to the images
    patterns = [
        r'//i\.4cdn\.org/([^/]+)/(\d+\.(jpg|png|gif|webm|mp4))',
        r'https?://i\.4cdn\.org/([^/]+)/(\d+\.(jpg|png|gif|webm|mp4))',
    ]
    
    found_images = set()
    for pattern in patterns:
        for match in re.finditer(pattern, html):
            board_name = match.group(1)
            filename = match.group(2)
            image_url = f'https://i.4cdn.org/{board_name}/{filename}'
            found_images.add((image_url, filename))
    
    print(f'Found images: {len(found_images)}')
    
    # thumbs
    thumb_pattern = r'//i\.4cdn\.org/([^/]+)/(\d+s\.jpg)'
    found_thumbs = set()
    for match in re.finditer(thumb_pattern, html):
        board_name = match.group(1)
        filename = match.group(2)
        thumb_url = f'https://i.4cdn.org/{board_name}/{filename}'
        found_thumbs.add((thumb_url, filename))
    
    print(f'Found thumbs: {len(found_thumbs)}')
    
    total_downloaded = 0
    total_files = len(found_images) + len(found_thumbs)
    current_file = 0
    
    # downloading images
    for image_url, filename in found_images:
        if cancel_check and cancel_check():
            print('Loading is cancelled')
            return False
            
        current_file += 1
        local_path = os.path.join(images_dir, filename)
        
        if not os.path.exists(local_path):
            try:
                img_response = requests.get(image_url, headers=headers, timeout=30)
                if img_response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(img_response.content)
                    file_size = len(img_response.content)
                    total_downloaded += file_size
                    print(f'Downloaded: {filename}')
                    
                    if progress_callback:
                        progress_callback(current_file, total_files, total_downloaded, filename)
                else:
                    print(f'Error {img_response.status_code} for {filename}')
                time.sleep(0.5)  # небольшая задержка между запросами
            except Exception as e:
                print(f'Error while downloading {filename}: {e}')
        
        html = html.replace(image_url, f'images/{filename}')
        html = html.replace(f'//{image_url.replace("https://", "")}', f'images/{filename}')
    
    # downlading thumbs
    for thumb_url, filename in found_thumbs:
        if cancel_check and cancel_check():
            print('Download cancelled')
            return False
            
        current_file += 1
        local_path = os.path.join(thumbs_dir, filename)
        
        if not os.path.exists(local_path):
            try:
                thumb_response = requests.get(thumb_url, headers=headers, timeout=30)
                if thumb_response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(thumb_response.content)
                    file_size = len(thumb_response.content)
                    total_downloaded += file_size
                    print(f'Finish downloading thumbnail: {filename}')
                    
                    if progress_callback:
                        progress_callback(current_file, total_files, total_downloaded, filename)
                time.sleep(0.5)
            except Exception as e:
                print(f'Error when downloading thumbnail {filename}: {e}')
        
        html = html.replace(thumb_url, f'thumbs/{filename}')
        html = html.replace(f'//{thumb_url.replace("https://", "")}', f'thumbs/{filename}')
    
    # removing unnecessarry elements
    soup = BeautifulSoup(html, 'html.parser')

    for bl_css in BLACKLISTED_CLASSES:
        for element in soup.find_all(class_=bl_css):
            element.decompose()

    for bl_id in BLACKLISTED_IDS:
        for element in soup.find_all(id=bl_id):
            element.decompose()

    html = str(soup)
    
    # saving html
    with open(os.path.join(thread_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'Thread saved to:  {thread_dir}')
    return True