from requests import get
from bs4 import BeautifulSoup
from os import path, makedirs
from PIL import Image
from io import BytesIO
from time import sleep
from random import randint
from re import sub

headers_image = {
    'Referer': "https://lectortmo.com/viewer/",
}

headers_html = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
              '*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alived',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}


def get_html_info(normal_url: str, headers) -> BeautifulSoup:
    """Use an Url of a website and convert it into Beautiful Soup"""
    req = get(normal_url, headers=headers).text
    soup = BeautifulSoup(req, features="html.parser")
    return soup


class TMOnline:
    """Class to download from TMO"""

    def __init__(self):
        print(
            "Hi this is a web scracher automatically downloads any series that you want from "
            "TMOnline using a link from its website")
        inp_link = input("Insert the link here: ")
        splited_code = inp_link.split('/')
        if splited_code[-1] == 'paginated':
            self.nuclear_code = splited_code[-2]
        elif splited_code[-2] == 'paginated':
            self.nuclear_code = splited_code[-3]
        else:
            print(
                "Invalid link try to make sure the link is formatted in this way: "
                "https://lectortmo.com/viewer/1ff69ca979d1d6357d7b27608850b56d/paginated")

        print(self.nuclear_code)
        first_link = f'https://lectortmo.com/viewer/{self.nuclear_code}/paginated/1'
        self.sauce_soup = get_html_info(first_link, headers=headers_html)
        self.get_images_loop(first_link)

    def get_images_loop(self, link: str):
        # First create the values that doesn't change before the loop and pass them into a dict
        page_obj = self.declare_variable(link)
        print(f"Number of pages: {page_obj['pag_num']}")
        for i in range(page_obj['pag_num'] + 2)[1:]:
            if i == page_obj['pag_num'] + 1:
                self.select_next_chapter()
            dynamic_name = f"{page_obj['path']}/{i}.{page_obj['img_type']}"
            if path.exists(dynamic_name):
                continue
            main_code = f"https://lectortmo.com/viewer/{self.nuclear_code}/paginated/{i}"
            headers_image['Referer'] = main_code
            sauce_soup = get_html_info(main_code, headers=headers_html)
            image_source = sauce_soup.find_all('img')[0]['src']
            print(image_source)
            r = get(image_source, headers=headers_image, stream=True)
            image = Image.open(BytesIO(r.content))
            image.save(dynamic_name)

            # Sleep for some time to avoid ban
            print(f"Downloading page {i} of {page_obj['pag_num']}")
            sleep_time = randint(1, 5)
            print(f"Shhh shasha is asleep for {sleep_time}")
            sleep(sleep_time)

    def create_path(self):
        false_title = str(self.sauce_soup.find_all('h1')[0].get_text())
        sauce_title = sub('[()\"\'#/@;:<>{}`+=~|.!?,]', '', false_title)
        tag = self.sauce_soup.find_all('b')[1].get_text()
        if tag == "ONE SHOT":
            path_local = f'images/{tag}/{sauce_title}'
        else:
            sauce_chapter = float(self.sauce_soup.find_all('h2')[0].get_text().split()[1])
            path_local = f'images/{tag}/{sauce_title}/Chapter {sauce_chapter}'
            print(f"Chap {sauce_chapter}!!!")
        print(path_local)
        if not path.exists(path_local):
            makedirs(path_local)

        return path_local

    def select_next_chapter(self):
        # It's a useless link that only redirect you to the actual page
        false_link = str(self.sauce_soup.findAll(
            class_="col-6 col-sm-2 order-2 order-sm-3 chapter-arrow chapter-next")).split('"')[3]
        # Uses next_link to get it's redirection to the actual link
        redirect_link = get(false_link, headers=headers_html)
        print(f"Being redirected from to {false_link}: to {redirect_link.url}")
        self.nuclear_code = redirect_link.url.split('/')[-2]
        # If we send the raw redirect link will throw an error so we need to format it
        next_link = f'https://lectortmo.com/viewer/{self.nuclear_code}/paginated/1'
        print(next_link)
        self.get_images_loop(next_link)

    def declare_variable(self, link):
        """Takes the value that doesn't change on the loop"""
        self.sauce_soup = get_html_info(link, headers=headers_html)
        page_number = int(self.sauce_soup.findAll('select')[0].get_text().split('\n')[-2])
        image_type = self.sauce_soup.find_all('img')[0]['src'].split('.')[-1]
        path_local = self.create_path()
        return {'pag_num': page_number, 'img_type': image_type, 'path': path_local}


if __name__ == "__main__":
    tmonline = TMOnline()
    tmonline.select_next_chapter()
