import shutil

def main(specif_path, seeding_folder, new_title):
    destination_path = f"{seeding_folder}\{new_title}"
    shutil.move(specif_path, destination_path)
    return destination_path