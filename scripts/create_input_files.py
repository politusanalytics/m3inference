import sys
import re
import json
import os.path
import logging
from m3inference.preprocess import resize_imgs, update_json

extension_list = [".bmp", ".gif", ".GIF", ".Jpeg", ".JPEG", ".jpg", ".JPG", ".png", ".PNG"]

# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    json_file = sys.argv[1]
    img_dir = sys.argv[2]
    resized_img_dir = sys.argv[3]
    output_dir = sys.argv[4]


    # Should only be run once
    resize_imgs(img_dir, resized_img_dir)


    with open(json_file, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    file_without_images = open(output_dir + "/input_without_images.json", "w", encoding="utf-8")
    file_with_images = open(output_dir + "/input_with_images.json", "w", encoding="utf-8")

    for d in data:
        img_path = ""
        if d["pp"].strip():
            img_path = re.sub(r"^[^\/]+\/([^\/]+)$", "\g<1>", d["pp"].strip().replace("_normal", "_400x400"))
            for ex in extension_list:
                img_path = img_path.replace(ex, ".jpeg")

            if not img_path.endswith(".jpeg"):
                print("PROBLEM" + img_path)
                img_path += ".jpeg"

            img_path = resized_img_dir + "/" + img_path
            if not os.path.exists(img_path):
                img_path = ""

        if img_path:
            out_d = {"id": d["id_str"], "name": d["name"], "screen_name": d["screen_name"], "description": d["description"], "lang": "tr", "img_path": img_path}
            file_with_images.write(json.dumps(out_d) + "\n")
        else:
            out_d = {"id": d["id_str"], "name": d["name"], "screen_name": d["screen_name"], "description": d["description"], "lang": "tr"}
            file_without_images.write(json.dumps(out_d) + "\n")

    file_without_images.close()
    file_with_images.close()
