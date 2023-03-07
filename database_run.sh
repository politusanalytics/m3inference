path_to_output_image_folder=$1
path_to_another_output_image_folder=$2

# Preprocessing
python scripts/download_images.py database $path_to_output_image_folder $path_to_another_output_image_folder

# Run models
python use_model_for_database.py $path_to_another_output_image_folder
