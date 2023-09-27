import shutil, os

def main(specif_path, seeding_folder, new_title):
    if os.name == 'nt':
        os_character = "\\"
    else:
        os_character = "/"
    destination_path = f"{seeding_folder}{os_character}{new_title}"
    shutil.move(specif_path, destination_path)
    return destination_path