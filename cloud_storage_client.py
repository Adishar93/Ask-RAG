import os
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket("helpful-helper-404206.appspot.com")


def upload_file_to_location(file_directory, file_name, storage_path):
    blob = bucket.blob(storage_path)
    blob.upload_from_filename(os.path.join(file_directory, file_name))


def download_file_from_location(file_directory, file_name, storage_path):
    blob = bucket.blob(storage_path)
    os.makedirs(file_directory, exist_ok=True)
    blob.download_to_filename(os.path.join(file_directory, file_name))
