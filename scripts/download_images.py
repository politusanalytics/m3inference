import requests
import shutil
import sys
import re
import json
from time import time
import os.path

if __name__ == "__main__":
    json_file = sys.argv[1]
    output_dir = sys.argv[2]

    with open(json_file, "r", encoding="utf-8") as f:
        image_urls = []
        for line in f:
            d = json.loads(line)
            if d["pp"].strip():
                image_urls.append(d["pp"].strip().replace("_normal", "_400x400"))

    print("Number of files with image urls: {}".format(len(image_urls)))
    stime = time()
    for url in image_urls:
        download_url = "https://pbs.twimg.com/profile_images/" + url
        filename = re.sub(r"^[^\/]+\/([^\/]+)$", "\g<1>", url)
        path = output_dir + "/" + filename

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
