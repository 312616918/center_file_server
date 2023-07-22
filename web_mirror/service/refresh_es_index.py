import re

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from common.db_util import web_info_clt
from common.es_util import es
from file_core.service.file_core import get_file_content


def refresh_web_info(process_callback=None):
    # 从mongodb中获取所有的web_info
    size = web_info_clt.estimated_document_count({})

    info_list = web_info_clt.find()

    def gen():
        idx = 0
        for info in info_list:
            html = get_file_content(info["html_file_id"])
            bs = BeautifulSoup(html, 'html.parser')
            content = bs.get_text()
            content = re.sub(r"\s+", " ", content)
            yield {
                "_index": "web_info_2023_07_16",
                "_id": str(info["_id"]),
                "_source": {
                    "title": info["title"],
                    "url": info["url"],
                    "content": content,
                    "create_time": info.get("create_time", ""),
                }
            }
            idx += 1
            print("refresh_web_info:", idx, size)
            if process_callback:
                process_callback(idx, size)

    helpers.bulk(es, gen())


if __name__ == '__main__':
    refresh_web_info()