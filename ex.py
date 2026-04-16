from openimages.download import download_dataset

download_dataset(
    "train",                      # dataset split
    ["Person", "Car", "Dog", "Chair", "Table"],  # classes
    limit=200
)