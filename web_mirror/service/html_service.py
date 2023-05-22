import io
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bson import ObjectId
from flask import send_file

from common.db_util import web_info_clt
from file_core.service.file_core import create_file, get_file_content
from web_mirror.engine.crawler_core import BaseCrawler
from web_mirror.engine.web_engine import WebEngine

RES_ATTR_DICT = {
    "img": "src",
    "link": "href",
    "script": "src",
}

base_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
}


def save_web_from_engine(url):
    engine = WebEngine()
    page_info = engine.get_info(url)
    html = page_info["html"]
    engine.close()

    bs = BeautifulSoup(html, 'html.parser')
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
                full_url = urljoin(url, origin_url)

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


            # save resource
            file_id = create_file(origin_url.split("/")[-1], resp.content)
            src_info_list.append({
                "name": name,
                "attr_name": attr_name,
                "origin_url": origin_url,
                "full_url": full_url,
                "file_id": file_id
            })

    title = page_info["title"]

    html_file_id = create_file(title, html.encode())
    screenshot_file_id = create_file(title + ".png", page_info["screenshot"])

    web_id = web_info_clt.insert_one({
        "title": title,
        "url": url,
        "create_time": datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
        "html_file_id": html_file_id,
        "src_info": src_info_list,
        "screenshot_file_id": screenshot_file_id,
    })
    return str(web_id.inserted_id)


def get_html_by_web_id(web_id, res_url_prefix):
    # read web html
    web_info = web_info_clt.find_one({"_id": ObjectId(web_id)})
    if not web_info:
        return None
    html = get_file_content(web_info["html_file_id"])
    bs = BeautifulSoup(html, 'html.parser')

    url_file_id_dict = {}
    for item in web_info["src_info"]:
        url_file_id_dict[item["origin_url"]] = str(item["file_id"])

    for name in RES_ATTR_DICT:
        attr_name = RES_ATTR_DICT[name]
        for label in bs.find_all(name):
            if attr_name not in label.attrs:
                continue

            # replace_url
            origin_url = label.attrs[attr_name]
            file_id = url_file_id_dict.get(origin_url, None)
            if not file_id:
                continue
            new_url = res_url_prefix + file_id
            if re.search(r"\.[a-zA-Z0-9]+$", origin_url):
                new_url += origin_url[origin_url.rfind("."):]
            label.attrs[attr_name] = new_url
    for tag in bs.find_all("script"):
        tag.decompose()
    for tag in bs.find_all("img"):
        del tag["onerror"]
    return bs.prettify()


def get_src_content(src_url):
    re_ids = re.findall(r"/([0-9a-fA-F]{24})(\.[a-zA-Z0-9]+)?$", src_url)
    if not re_ids:
        return None
    file_id = re_ids[0][0]
    content = get_file_content(file_id)
    return send_file(io.BytesIO(content), download_name=src_url.split("/")[-1], as_attachment=True)
    # return get_file_content(file_id)


def get_all_web_info():
    info_list = web_info_clt.find().sort("create_time", -1).limit(1000)
    result_list = []
    for info in info_list:
        result_list.append({
            "id": str(info["_id"]),
            "title": info["title"],
            "url": info["url"],
            "create_time": info.get("create_time"),
        })
    return result_list

def save_web_by_html(info):
    crawler = BaseCrawler(info)
    return crawler.run()