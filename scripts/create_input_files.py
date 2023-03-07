import sys
import re
import json
import os.path
import logging
from m3inference.preprocess import resize_imgs, update_json
import gzip

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    json_file_or_database = sys.argv[1] # can be a json file or "database"
    resized_img_dir = sys.argv[2]
    output_dir = sys.argv[3]

    # with open(json_file, "r", encoding="utf-8") as f:
    with gzip.open(json_file, "rt", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    file_without_images = open(output_dir + "/input_without_images.json", "w", encoding="utf-8")
    file_with_images = open(output_dir + "/input_with_images.json", "w", encoding="utf-8")

    for d in data:
        img_path = resized_img_dir + "/" + d["id_str"] + ".jpeg"
        if os.path.exists(img_path):
            out_d = {"id": d["id_str"], "name": d["name"], "screen_name": d["screen_name"], "description": d["description"], "lang": "tr", "img_path": img_path}
            file_with_images.write(json.dumps(out_d) + "\n")
        else:
            out_d = {"id": d["id_str"], "name": d["name"], "screen_name": d["screen_name"], "description": d["description"], "lang": "tr"}
            file_without_images.write(json.dumps(out_d) + "\n")

    file_without_images.close()
    file_with_images.close()
