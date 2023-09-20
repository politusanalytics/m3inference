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

    if json_file_or_database == "database":
        # Connect to mongodb
        import pymongo
        mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = mongo_client["politus_twitter"]
        # Get the collections(tables)
        user_col = db["users"]

        # NOTE: This part is for crontab job. It is so that a new job does not run this script while it is already running!
        num_currently_in_process = user_col.count_documents({"to_be_pp_processed": False})
        if num_currently_in_process > 0:
            raise(f"This script is already running somewhere else! Number of remaining profile pictures to download from the previous run: {num_currently_in_process}.")

        # NOTE: We mark what we will process. We do this to avoid discrepancies betweeen
        # this find and the find in "use_model_for_database.py"! We will unset this mark
        # once we finish in the prediction part.
        user_col.update_many({"$and": [{"demog_pred_full": None}, {"demog_pred_txt": None}],
                              "pp": {"$ne": None}, "to_be_pp_processed": None},
                             {"$set": {"to_be_pp_processed": False}})
        f = user_col.find({"to_be_pp_processed": False}, ["pp"])

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
        if row["pp"].strip() not in ["", "default_profile_images/default_profile_normal.png"]:
            image_urls.append((row["_id"], row["pp"].strip().replace("_normal", "_400x400")))
        else:
            # TODO: Should these be removed from database?
            user_col.update_one({"_id": row["_id"]}, {"$unset": {"to_be_pp_processed": ""}})

    if json_file_or_database != "database":
        f.close()

    print("Number of files with image urls: {}".format(len(image_urls)))
    stime = time()
    for id_str, url in image_urls:
        download_url = "https://pbs.twimg.com/profile_images/" + url
        out_path = output_dir + "/" + id_str + ".jpeg"
        resized_out_path = resized_img_dir + "/" + id_str + ".jpeg"

        if (not os.path.exists(out_path)) and (not os.path.exists(resized_out_path)): # if not downloaded before
            try:
                r = requests.get(download_url, stream=True) # settings.STATICMAP_URL.format(**data)
                if r.status_code == 200:
                    with open(out_path, 'wb') as f:
                        # r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
            except:
                print("Could not download: {}".format(url))

        user_col.update_one({"_id": id_str}, {"$set": {"to_be_pp_processed": True}})

    etime = time()
    diff = etime - stime
    print("Download time took {} seconds in total.".format(diff))

    # Resize images
    resize_imgs(output_dir, resized_img_dir)
