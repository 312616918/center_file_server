import os

from gridfs import GridFS
from pymongo import MongoClient

mongo_url = os.environ.get("MONGO_URL")

mg_client = MongoClient(mongo_url)
db = mg_client["center_file"]
file_info_clt = db["file_info"]
gfs = GridFS(db)

web_info_clt = db["web_info"]

