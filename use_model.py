from time import time
from m3inference import M3Inference
import json
import sys

if __name__ == "__main__":
    input_file = sys.argv[1]
    only_text = sys.argv[2] == "true"
    output_filename = sys.argv[3]

    batch_size = 2048

    use_full_model = not only_text

    model_load_start = time()
    m3 = M3Inference(use_full_model=use_full_model, parallel=True)
    model_load_end = time()
    pred = m3.infer(input_file, batch_size=batch_size)
    pred_end = time()

    with open(output_filename, "w") as f:
        for k, v in pred.items():
            d = {"id": k, "isFemale": v["gender"]["female"], "isOrg": v["org"]["is-org"]}
            age = v["age"]
            d["age"] = [age["<=18"], age["19-29"], age["30-39"], age[">=40"]]
            f.write(json.dumps(d, sort_keys=True) + "\n")

    write_end = time()

    model_load_time = model_load_start - model_load_end
    pred_time = model_load_end - pred_end
    write_time = pred_end - write_end
    print("Model loading: %.2f, Prediction: %.2f, Writing: %.2f" %(model_load_time, pred_time, write_time))
