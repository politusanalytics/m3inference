from time import time
from m3inference import M3Inference
import json
import sys
import re
import os.path
import pymongo
import dateutil.parser

resized_img_dir = sys.argv[1]

batch_size = 2048 # 3072 took the same time for 400k samples

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["politus_twitter"]
# Get the collections(tables)
user_col = db["users"]

def run_model_and_write(input_data, use_full_model):
    model_load_start = time()
    m3 = M3Inference(use_full_model=use_full_model, parallel=True)
    model_load_end = time()
    pred = m3.infer(input_data, batch_size=batch_size)
    pred_end = time()

    for k, v in pred.items():
        age = v["age"]
        age = [age["<=18"], age["19-29"], age["30-39"], age[">=40"]]
        p = {"age": age, "isFemale": v["gender"]["female"], "isOrg": v["org"]["is-org"], "version": 0}

        if use_full_model:
            out_d = {"demog_pred_full": p, "demog_pred_txt": {}}
        else:
            out_d = {"demog_pred_full": {}, "demog_pred_txt": p}

        # write to database
        user_col.update_one({"_id": k}, {"$set": out_d, "$unset": {"to_be_pp_processed": ""}})
        # out_file.write(json.dumps({k: out_d}) + "\n")

    write_end = time()

    model_load_time = model_load_start - model_load_end
    pred_time = model_load_end - pred_end
    write_time = pred_end - write_end
    print("Model loading: %.2f, Prediction: %.2f, Writing: %.2f" %(model_load_time, pred_time, write_time))


if __name__ == "__main__":
    result = user_col.find({"to_be_pp_processed": True}, ["name", "screen_name", "description"])

    full_model_in_data = []
    only_text_model_in_data = []
    for res_idx, row in enumerate(result):
        row["id"] = row["_id"]
        row["lang"] = "tr"
        row.pop("_id")

        img_path = resized_img_dir + "/" + row["id"] + ".jpeg"
        if os.path.exists(img_path):
            row["img_path"] = img_path
            full_model_in_data.append(row)
        else:
            only_text_model_in_data.append(row)

    print(f"Full data size: {len(full_model_in_data)}")
    print(f"Text only data size: {len(only_text_model_in_data)}")
    print(f"Total data size: {res_idx}")

    # full model
    if len(full_model_in_data) > 0:
        run_model_and_write(full_model_in_data, True)

    # text model
    if len(only_text_model_in_data) > 0:
        run_model_and_write(only_text_model_in_data, False)
