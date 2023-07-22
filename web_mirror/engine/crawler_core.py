from datetime import datetime
from urllib.parse import urljoin

import cacheout
import requests
from bs4 import BeautifulSoup

from common.db_util import web_info_clt
from file_core.service.file_core import create_file


base_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
}

def get_or_replace_label_urls(label, label_name, url_dict):
    url_list = []
    if label_name == "img":
        if "src" in label.attrs:
            url = label.attrs["src"]
            url_list.append(url)
            if url_dict and url in url_dict:
                label.attrs["src"] = url_dict[url]
        if "data-src" in label.attrs:
            url = label.attrs["data-src"]
            url_list.append(url)
            if url_dict and url in url_dict:
                label.attrs["data-src"] = url_dict[url]
        if "srcset" in label.attrs:
            src_set = label.attrs["srcset"]
            replace_src_set = []
            for src in src_set.split(","):
                sp = src.split(" ")
                url = sp[0].strip()
                url_list.append(url)
                if url_dict and url in url_dict:
                    replace_src_set.append(" ".join([url_dict[url], sp[1]]))
                else:
                    replace_src_set.append(src)
            if url_dict:
                label.attrs["srcset"] = ",".join(replace_src_set)
        if "data-srcset" in label.attrs:
            src_set = label.attrs["data-srcset"]
            replace_src_set = []
            for src in src_set.split(","):
                sp = src.split(" ")
                url = sp[0].strip()
                url_list.append(url)
                if url_dict and url in url_dict:
                    replace_src_set.append(" ".join([url_dict[url], sp[1]]))
                else:
                    replace_src_set.append(src)
            if url_dict:
                label.attrs["data-srcset"] = ",".join(replace_src_set)
        return url_list
    if label_name == "link":
        if "href" in label.attrs:
            url = label.attrs["href"]
            url_list.append(url)
            if url_dict and url in url_dict:
                label.attrs["href"] = url_dict[url]
        return url_list
    if label_name == "script":
        if "src" in label.attrs:
            url = label.attrs["src"]
            url_list.append(url)
            if url_dict and url in url_dict:
                label.attrs["src"] = url_dict[url]
        return url_list
    return url_list

@cacheout.memoize(ttl=60 * 10, maxsize=1000)
def download_resource(url):
    try:
        resp = requests.get(url=url, headers=base_header)
        if resp.status_code != 200:
            print("can't download:", url)
            return None
        print("downloaded:", url)
        return resp.content
    except Exception as e:
        print(e)
        print("can't download:", url)
        return None


class BaseCrawler():
    def __init__(self, info: {}):
        self.info = info

    def run(self):
        if self.info.get("skip_same_url", False):
            if web_info_clt.find_one({"url": self.info["url"]}):
                return

        if not "html" in self.info:
            self.set_info()
        return self.save_resource()

    def set_info(self):
        resp = requests.get(url=self.info["url"], headers=base_header)
        self.info["html"] = resp.text

    def save_resource(self):
        bs = BeautifulSoup(self.info["html"], 'html.parser')
        src_info_list = []
        for name in ["img", "link", "script"]:
            for label in bs.find_all(name):
                for origin_url in get_or_replace_label_urls(label, name, None):
                    if not origin_url or not origin_url.strip():
                        continue
                    print(origin_url)
                    if origin_url.startswith("http"):
                        full_url = origin_url
                    else:
                        full_url = urljoin(self.info["url"], origin_url)

                    # download resource
                    res_content = download_resource(full_url)
                    if not res_content:
                        continue

                    # save resource
                    file_id = create_file(origin_url.split("/")[-1], res_content)
                    src_info_list.append({
                        "name": name,
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
