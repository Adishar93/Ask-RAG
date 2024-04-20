import os


def write_file(file_path, file_contents):
    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)

    # Write the file to disk
    with open(file_path, "wb") as file:
        file.write(file_contents)
