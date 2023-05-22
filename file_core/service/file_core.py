"""
文件核心，作为文件的基础服务
"""
import hashlib
import os
from datetime import datetime

from bson import ObjectId

from common.db_util import file_info_clt, gfs


def create_file(file_name, content):
    md5_alg = hashlib.md5()
    md5_alg.update(content)
    md5 = md5_alg.hexdigest()

    sha256_alg = hashlib.sha256()
    sha256_alg.update(content)
    sha256 = sha256_alg.hexdigest()

    content_len = len(content)

    exist_file_info = file_info_clt.find_one({"md5": md5, "sha256": sha256, "content_len": content_len})
    if exist_file_info:
        print("file exist:", file_name)
        return str(exist_file_info["_id"])

    gfs_id = gfs.put(content, filename=file_name)
    file_id = file_info_clt.insert_one({
        "origin_name": file_name,
        "md5": md5,
        "sha256": sha256,
        "content_len": content_len,
        "gfs_id": gfs_id,
        "create_time": datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    })
    return str(file_id.inserted_id)


def get_file_content(file_id):
    if type(file_id) != ObjectId:
        file_id = ObjectId(file_id)
    file_info = file_info_clt.find_one({"_id": file_id})
    if not file_info:
        return None
    return gfs.get(file_info["gfs_id"]).read()


if __name__ == '__main__':
    file_id = create_file("test_file.txt", "this is a file for test".encode())
    print(get_file_content(file_id))
