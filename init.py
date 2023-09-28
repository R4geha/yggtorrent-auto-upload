import mediainfo, json, os

tracker_url = "http://connect.drago-server.org:8080/xxxxxxxxxxxxxxxxxx/announce"
tmdb_api_key = ''
yggtorrent_url = 'https://yggtorrent.wtf'
yggtorrent_user = ''
yggtorrent_password = ''
seeding_folder = r"Z:\Vidéos\Seeding" # Où seront stockés les dossiers/ fichiers pour le seeding
torrent_folder = r"Z:\Vidéos\Seeding\0 - TORRENT FILES" # Où seront stockés les fichiers .torrent
nfo_folder = r"Z:\Vidéos\Seeding\1 - NFO FILES" # Où seront stockés les fichiers nfo
root_path = r"Z:\Vidéos\Downloaded" # Où sont les dossiers/ fichiers téléchargés
tag = "" # Si vous souhaitez mettre votre tag ou celui de votre team (laisser à vide si vous souhaitez ne pas en mettre)

with open("titles.json", "r", encoding="utf-8") as json_file:
    data_titles = json.load(json_file)
    
mediainfo.main(tracker_url, seeding_folder, torrent_folder, nfo_folder, tmdb_api_key, data_titles, yggtorrent_user, yggtorrent_password, yggtorrent_url, root_path, tag)
