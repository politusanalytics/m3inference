path_to_input_json_file=$1
path_to_output_image_folder=$2
path_to_another_output_image_folder=$3
# Files named "input_without_images.json" and "input_with_images.json" in this folder
# will be overwritten in scripts/create_input_files.py script.
path_to_output_folder=$4

# Preprocessing
python scripts/download_images.py $path_to_input_json_file $path_to_output_image_folder
python scripts/create_input_files.py $path_to_input_json_file $path_to_output_image_folder $path_to_another_output_image_folder $path_to_output_folder

# Model runs
python use_model.py $path_to_output_folder/input_without_images.json true $path_to_output_folder/only_text_model_predictions.json
python use_model.py $path_to_output_folder/input_with_images.json false $path_to_output_folder/full_model_predictions.json
