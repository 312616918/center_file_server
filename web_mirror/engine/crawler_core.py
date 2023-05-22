from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from common.db_util import web_info_clt
from file_core.service.file_core import create_file

RES_ATTR_DICT = {
    "img": "src",
    "link": "href",
    "script": "src",
}
base_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
}


class BaseCrawler():
    def __init__(self, info: {}):
        self.info = info

    def run(self):
        if not "html" in self.info:
            self.set_info()
        return self.save_resource()

    def set_info(self):
        resp = requests.get(url=self.info["url"], headers=base_header)
        self.info["html"] = resp.text

    def save_resource(self):
        bs = BeautifulSoup(self.info["html"], 'html.parser')
        src_info_list = []
        for name in RES_ATTR_DICT:
            attr_name = RES_ATTR_DICT[name]
            for label in bs.find_all(name):
                if attr_name not in label.attrs:
                    continue
                # gen_url
                origin_url = label.attrs[attr_name]
                print(origin_url)
                if origin_url.startswith("http"):
                    full_url = origin_url
                else:
                    full_url = urljoin(self.info["url"], origin_url)

                # download resource
                try:
                    resp = requests.get(url=full_url, headers=base_header)
                    if resp.status_code != 200:
                        print("can't download:", full_url)
                        continue
                    print("downloaded:", origin_url)
                except Exception as e:
                    print(e)
                    print("can't download:", full_url)
                    continue

                # save resource
                file_id = create_file(origin_url.split("/")[-1], resp.content)
                src_info_list.append({
                    "name": name,
                    "attr_name": attr_name,
                    "origin_url": origin_url,
                    "full_url": full_url,
                    "file_id": file_id
                })

        title = bs.title.text

        html_file_id = create_file(title, self.info["html"].encode())
        # screenshot_file_id = create_file(title + ".png", page_info["screenshot"])

        self.info.update({
            "title": title,
            "create_time": datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
            "html_file_id": html_file_id,
            "src_info": src_info_list,
            # "screenshot_file_id": screenshot_file_id,
        })
        web_id = web_info_clt.insert_one(self.info)
        return str(web_id.inserted_id)
