import requests
import shutil
import sys
import re
import json
from time import time
import os.path
import gzip
from m3inference.preprocess import resize_imgs
import dateutil.parser

if __name__ == "__main__":
    json_file_or_database = sys.argv[1] # can be a json file or "database"
    output_dir = sys.argv[2]
    resized_img_dir = sys.argv[3]

    # start_date = "2022-09-01"
    if json_file_or_database == "database":
        # Connect to mongodb
        import pymongo
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = mongo_client["politus_twitter"]
        # Get the collections(tables)
        user_col = db["users"]

        #"tweets": {"$elemMatch": {"date": {"$gte": dateutil.parser.parse(start_date)}}},
        f = user_col.find({"$and": [{"demog_pred_full": None}, {"demog_pred_txt": None}],
                           "pp": {"$ne": None}}, ["pp"])

    elif json_file_or_database.endswith(".json.gz"):
        f = gzip.open(json_file_or_database, "rt", encoding="utf-8")
    elif json_file_or_database.endswith(".json"):
        f = open(json_file_or_database, "r", encoding="utf-8")
    else:
        raise("Wrong extension for the input file!")

    image_urls = []
    for row in f:
        if json_file_or_database != "database":
            row = json.loads(row)
            row["_id"] = row["id_str"]
        if row["pp"].strip():
            image_urls.append((row["_id"], row["pp"].strip().replace("_normal", "_400x400")))

    if json_file_or_database != "database":
        f.close()

    print("Number of files with image urls: {}".format(len(image_urls)))
    stime = time()
    for id_str, url in image_urls:
        download_url = "https://pbs.twimg.com/profile_images/" + url
        path = output_dir + "/" + id_str + ".jpeg"

        try:
            r = requests.get(download_url, stream=True) # settings.STATICMAP_URL.format(**data)
            if r.status_code == 200 and not os.path.exists(path):
                with open(path, 'wb') as f:
                    # r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        except:
            print("Could not download: {}".format(url))

    etime = time()
    diff = etime - stime
    print("Download time took {} seconds in total.".format(diff))


    # Resize images
    resize_imgs(output_dir, resized_img_dir)
