import json
import os
import re
from urllib.parse import urlparse

import sys
from bs4 import BeautifulSoup

import requests


def grab_images_from_imgurl(target_url):
    response = requests.get(url=target_url)
    if response.status_code != 200:
        print('Something went wrong. Maybe wrong url')
    content = response.content

    soup = BeautifulSoup(content, 'html.parser')

    script_source = soup.find('script', text=re.compile(r'window.runSlots'))

    content_str = str(script_source).replace('\n', '').split('window.runSlots = ', 1)[-1].rsplit('           };', 1)[
                      0] + '}'
    content_str = content_str.replace('config:', '"config":').replace('item:', '"item":')
    data_content = json.loads(content_str)

    img_urls = get_img_urls(data_content)
    image_folder_name = title(data_content)
    folder_for_images = os.path.join(os.path.dirname(__file__), image_folder_name)
    if not os.path.exists(folder_for_images):
        os.makedirs(folder_for_images)

    save_imgs(img_urls, folder_for_images)


def title(data_content: json) -> str:
    return data_content['item']['title']


def get_img_urls(data_content: dict) -> list:
    urls = []
    for img in data_content['item']['album_images']['images']:
        url = 'http://i.imgur.com/{hash}{ext}'.format(hash=img['hash'], ext=img['ext'])
        urls.append(url)
    return urls


def save_imgs(urls: list, target_folder: str) -> None:
    for url in urls:
        filename = os.path.join(target_folder, urlparse(url).path[1:])
        response = requests.get(url)
        if response.status_code != 200:
            print("Can't download {}".format(url))
        img_source = response.content
        with open(filename, 'bw') as img_file:
            img_file.write(img_source)
            print("File {} saved".format(filename))


if __name__ == '__main__':
    last_arg = sys.argv[-1]
    if 'imgur.com' not in last_arg:
        target_url = 'http://imgur.com/a/JioJm?grid'
    else:
        target_url = last_arg
        if not target_url.endswith('grid'):
            target_url += '?grid'

    grab_images_from_imgurl(target_url)
