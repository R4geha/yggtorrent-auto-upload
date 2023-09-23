import os
from pymediainfo import MediaInfo
import math, tmdb, organize_file, yggtorrent, subprocess, re



def calculate_total_size(path):
    if os.path.isdir(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size / (1024 * 1024 * 1024)
    elif os.path.isfile(path):
        return os.path.getsize(path) / (1024 * 1024 * 1024)
    else:
        return 0 

def process_folder(path, language):
    video_files = [f for f in os.listdir(path) if f.lower().endswith(('.mkv', '.mp4'))]
    if not video_files:
        subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        for subdir in subdirs:
            subdir_path = os.path.join(path, subdir)
            video_files = [f for f in os.listdir(subdir_path) if f.lower().endswith(('.mkv', '.mp4'))]
            if video_files:
                path = subdir_path
                break
        
    total_files = len(video_files)
    if total_files == 0:
        print("Aucun fichier mkv ou mp4 trouvé dans le dossier.")
        return
    
    total_size_gb = calculate_total_size(path)
    total_size = f"{total_size_gb:.2f}"
    
    total_video_bitrate = 0

    for video_file in video_files:
        file_path = os.path.join(path, video_file)
        video_info = get_video_info(file_path, language)   
        video_bitrate_digits = "".join(filter(str.isdigit, video_info['Débit vidéo']))
        if video_bitrate_digits:
            total_video_bitrate += int(video_bitrate_digits)
        
    average_video_bitrate = f"~{math.ceil(total_video_bitrate / len(video_files))}"
    bbcode_output, title_channels, title_codec, title_height, title_language, title_hdr = generate_bbcode(video_info, total_files, total_size, average_video_bitrate)
    return bbcode_output, title_channels, title_codec, title_height, title_language, title_hdr
        
def get_video_info(file_path, language):
    media_info = MediaInfo.parse(file_path)
    for track in media_info.tracks:
        if track.track_type == "Video" and track.other_hdr_format:
            for hdr_format in track.other_hdr_format:
                if "hdr" in hdr_format.lower():
                    hdr_info = "HDR."
        elif track.track_type == "Video":
            hdr_info = ""
            
    video_info = {
        "Taille": os.path.getsize(file_path) / (1024 * 1024 * 1024),
        "Type de fichier": os.path.splitext(file_path)[1][1:].upper(),
        "Débit global moyen": media_info.tracks[0].other_overall_bit_rate[0] if media_info.tracks and media_info.tracks[0].other_overall_bit_rate else "N/A",
        "Débit vidéo": media_info.tracks[1].other_bit_rate[0] if len(media_info.tracks) > 1 and media_info.tracks[1].other_bit_rate else "N/A",
        "Format vidéo": media_info.tracks[1].format if len(media_info.tracks) > 1 else "N/A",
        "Résolution vidéo": "1080p" if media_info.tracks[1].height >= 1080 else "720p",
        "HDR": hdr_info,
        "Path": file_path,
        "Pistes audios": [],
        "Sous-titres": [],
    }
    
    for track in media_info.tracks:
        if track.track_type == "Audio":
            audio_info = {
                "Format audio": track.format,
                "Débit audio": track.other_bit_rate[0] if track.other_bit_rate else "N/A",
                "Nombre de canaux": track.channel_s if track.channel_s else "N/A",
                "Langue": get_audio_language(track.other_language[0] if track.other_language else None, language, track.title if track.title else None),
            }
            video_info["Pistes audios"].append(audio_info)
        
        elif track.track_type == "Text" and track.title is not None:
            subtitle_info = {
                "Langue": get_subtitle_language(track.other_language[0] if track.other_language else None, language),
                "Type": track.title,
                "Writing": "Text/SRT" if track.writing_library and "srt" in track.writing_library.lower() else ""
            }
            if "Forced" in track.title:
                subtitle_info["Forced"] = "Yes"
            elif track.forced == "No":
                subtitle_info["Forced"] = "No"
            elif track.forced == "Yes":
                subtitle_info["Forced"] = "Yes"
            video_info["Sous-titres"].append(subtitle_info)
    
    return video_info

def get_audio_language(other_language, language, title):
    if other_language is None:
        return "Unknown"
    elif "French" in other_language or (title is not None and "français" in title):
        return "Français (VFF)"
    elif "English" in other_language or "anglais" in title:
        return "Anglais"
    elif "Japanese" in other_language:
        return "Japonais"
    elif "Hindi" in other_language:
        return "Hindi"
    elif "Telugu" in other_language:
        return "Télougou"
    elif "Korean" in other_language:
        return "Coréen"
    elif "Spanish" in other_language:
        return "Espagnol"
    elif "Swedish" in other_language or "suédois" in title:
        return "Suédois"
    else:
        return "Unknow"

def get_subtitle_language(other_language, language):
    if other_language is None:
        return "Unknown"
    elif "French" in other_language:
        return "Français (VFF)"
    elif "English" in other_language:
        return "Anglais"
    elif "Japanese" in other_language:
        return "Japonais"
    elif "Hindi" in other_language:
        return "Hindi"
    elif "Telugu" in other_language:
        return "Télougou"
    elif "Korean" in other_language:
        return "Coréen"
    elif "Spanish" in other_language:
        return "Espagnol"
    elif "Swedish" in other_language:
        return "Suédois"
    else:
        return "Unknow"

def generate_bbcode(video_info, total_files, total_size, average_video_bitrate):
    if video_info['Format vidéo'] == "AVC":
        codec_video = "AVC/x264/h.264" 
        title_codec = "x264"
    else:
        codec_video = "HEVC/x265/h.265"
        title_codec = "H265"

    title_height = f"WEB.{video_info['Résolution vidéo']}."
    bbcode_template = f"""
[img]https://i.imgur.com/fKYpxI3.png[/img]

[b]Qualité :[/b] WEB {video_info['Résolution vidéo']}
[b]Format :[/b] {video_info['Type de fichier']}
[b]Codec Vidéo :[/b] {codec_video}
[b]Débit Vidéo :[/b] {average_video_bitrate} kb/s

    
[b]Langue(s) :[/b]
"""
    audio_language_list = []
    for index, audio in enumerate(video_info["Pistes audios"], start=1):
        channels = f"[{audio['Nombre de canaux']}]"
        if audio["Nombre de canaux"] == 6:
            channels = "[5.1]"
            title_channels = "DDP5.1."
        elif audio["Nombre de canaux"] == 2:
            channels = "[2.0]"
            title_channels = ""
        elif audio["Nombre de canaux"] != "N/A":
            channels = ""
            title_channels = ""
        bbcode_template += f"[img]https://flagcdn.com/20x15/{get_language_flag(audio['Langue'])}.png[/img] {audio['Langue']} {channels} / {audio['Format audio']} à {audio['Débit audio']}\n"
        audio_language_list.append(f"{audio['Langue']}")
    if video_info["Sous-titres"]:
        bbcode_template += f"""
    
[b]Sous-titres :[/b]
"""
        for subtitle in video_info["Sous-titres"]:
            forced = "(forced)" if subtitle["Forced"] == "Yes" else "(full)"
            bbcode_template += f"[img]https://flagcdn.com/20x15/{get_language_flag(subtitle['Langue'])}.png[/img] {subtitle['Langue']} | {subtitle['Writing']} {forced}\n"
    if total_files == 1:
        bbcode_template += f"""
[b] Débit global moyen :[/b] {video_info['Débit global moyen']}
"""
    if "netflix" in video_info["Path"].lower():
        source_release = "NF"
    elif "amazon" in video_info["Path"].lower():
        source_release = "AMZN"
    else:
        source_release = "Unknow"
    bbcode_template += f"""
[img]https://i.imgur.com/pkRSjYw.png[/img]
    
[b]Source / Release :[/b] {source_release} / Streamfab
[b]Nombre de fichier(s) :[/b] {total_files}
[b]Poids Total :[/b] {total_size} Go


[url=https://yggland.fr/fervexprez/][img]https://i.imgur.com/Yupo77P.png[/img][/url][/center]
"""

    title_language = check_languages(audio_language_list)
    title_hdr = video_info['HDR']
    return bbcode_template, title_channels, title_codec, title_height, title_language, title_hdr

def check_languages(languages):
    has_french = any("francais" in lang.lower() or "french" in lang.lower() or "vff" in lang.lower() for lang in languages)
    if len(languages) == 1 and has_french:
        return "VFF."
    elif len(languages) > 1 and has_french:
        return "MULTI."
    elif (len(languages) > 1 and not has_french) or (len(languages) == 1 and not has_french):
        return "VOSTFR."
    else:
        return "Unknown."

def get_language_flag(langue):
    if "Français" in langue:
        return "fr"
    elif "Anglais" in langue:
        return "us"
    elif "Japonais" in langue:
        return "jp"
    elif "Hindi" in langue:
        return "hi"
    elif "Telugu" in langue:
        return "tl"
    elif "Coréen" in langue:
        return "kr"
    elif "Espagnol" in langue:
        return "es"
    elif "Suédois" in langue:
        return "se"
    else:
        return "ar"

def create_torrent(source_path, destination_torrent_path, tracker_url):
    command = [
        'py3createtorrent', 
        '-o', destination_torrent_path,
        '-t', tracker_url,
        '-P',
        '-c', "YggTorrent",
        '-f',
        source_path
    ]
    subprocess.run(command, check=True)

def generate_nfo(input_path, nfo_output_path):
    command = [
        'MediaInfo.exe',
        '--Output=NFO',
        input_path
    ]

    with open(nfo_output_path, 'w', encoding='utf-8') as nfo_file:
        subprocess.run(command, stdout=nfo_file, text=True)

def select_category():
    categories = [
        "Animation",
        "Animation Série",
        "Concert",
        "Documentaire",
        "Emission TV",
        "Film",
        "Série TV",
        "Spectacle"
    ]
    
    print("Choisissez une catégorie :")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")
    
    user_choice = int(input("Entrez le numéro de la catégorie : "))
    
    if 1 <= user_choice <= len(categories):
        chosen_category = categories[user_choice - 1]
        print(f"Vous avez choisi la catégorie : {chosen_category}")
        return int(user_choice)
    else:
        print("Choix invalide.")

def select_file_or_folder(path):
    print("#"*75)
    print("Choix du fichier ou dossier")
    print("#"*75)
    excluded_names = ["Amazon", "Netflix", "CanalPlus", "Crunchyroll", "Disney+", "YouTube", "Youtube Plus", "Channels", "Music", "Video"]

    items = []
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir not in excluded_names and not re.match(r"S0\d", dir):
                items.append((os.path.join(root, dir), "Dossier"))
        for file in files:
            items.append((os.path.join(root, file), "Fichier"))

    for index, (item, item_type) in enumerate(items, start=1):
        print(f"{index}. {item_type} : {os.path.basename(item)}")

    choice = int(input("Entrez le numéro du fichier ou du dossier à sélectionner : "))
    selected_item = items[choice - 1][0]

    return selected_item
            
def main(tracker_url, seeding_folder, torrent_folder, nfo_folder, tmdb_api_key, data_titles, yggtorrent_user, yggtorrent_password, yggtorrent_url, root_path):
    os.system('cls')
    simulate = input("Voulez-vous rechercher un film/ une série de maniere simuler: [Oui/Non]")
    os.system('cls')
    if simulate.lower() in ["oui", "yes", "y", "o", "1"]:
        print('#'*100)
        bbcode, new_title, genres = tmdb.main("folder", tmdb_api_key, data_titles)
        print(bbcode + "-"*75 + "\n" + new_title)
        exit()
    specif_path = select_file_or_folder(root_path)
    print(f"\nChemin sélectionné : {specif_path}\n")
    language = "fr"
    print('#'*100)
    if os.path.isdir(specif_path):
        bbcode_output, title_channels, title_codec, title_height, title_language, title_hdr = process_folder(specif_path, language)
        bbcode, new_title, genres = tmdb.main("folder", tmdb_api_key, data_titles)
        bbcode_description = bbcode + bbcode_output
        print('-'*100)
        print(bbcode_description)
        print('-'*100)
        print("\n" + new_title + title_language + title_height + title_channels + title_hdr + title_codec)
        new_title_without_format = new_title + title_language + title_height + title_channels + title_hdr + title_codec 
        destination_path = organize_file.main(specif_path, seeding_folder, new_title_without_format)
        # CREATION DU TORRENT
        destination_torrent_path = f"{torrent_folder}\{new_title_without_format}.torrent"
        create_torrent(destination_path, destination_torrent_path, tracker_url)
        # GENERATE NFO
        nfo_output_path = f"{nfo_folder}\{new_title_without_format}.nfo"
        generate_nfo(destination_path, nfo_output_path)
        # CHOIX CATEGORIE
        chosen_category = select_category()
        # YGG AUTO-UPLOAD
        yggtorrent.init(destination_path, bbcode_description, new_title_without_format, chosen_category, nfo_output_path, destination_torrent_path, genres, yggtorrent_user, yggtorrent_password, yggtorrent_url)
    elif os.path.isfile(specif_path):
        total_size = f"{calculate_total_size(specif_path):.2f}"
        video_info = get_video_info(specif_path, language)
        if video_info['Débit vidéo'] == "N/A":
            average_video_bitrate = 0
        else:
            average_video_bitrate = math.ceil(int("".join(filter(str.isdigit, video_info['Débit vidéo']))))
        bbcode_output, title_channels, title_codec, title_height, title_language, title_hdr = generate_bbcode(video_info, 1, total_size, average_video_bitrate)
        bbcode, new_title, genres = tmdb.main("file", tmdb_api_key, data_titles)
        print('-'*100)
        print(bbcode + bbcode_output)
        print('-'*100)
        print("\n" + new_title + title_language + title_height + title_channels + title_hdr + title_codec)
        ygg_new_title = new_title
        file_extension = os.path.basename(specif_path).split('.')[-1]
        new_title = new_title + title_language + title_height + title_channels + title_hdr + title_codec + "." + file_extension
        new_title_without_format = ygg_new_title + title_language + title_height + title_channels + title_hdr + title_codec 
        bbcode_description = bbcode + bbcode_output
        destination_path = organize_file.main(specif_path, seeding_folder, new_title)
        # CREATION DU TORRENT
        destination_torrent_path = f"{torrent_folder}\{new_title}.torrent"
        create_torrent(destination_path, destination_torrent_path, tracker_url)
        # GENERATE NFO
        nfo_output_path = f"{nfo_folder}\{new_title}.nfo"
        generate_nfo(destination_path, nfo_output_path)
        # CHOIX CATEGORIE
        chosen_category = select_category()
        # YGG AUTO-UPLOAD
        yggtorrent.init(destination_path, bbcode_description, new_title_without_format, chosen_category, nfo_output_path, destination_torrent_path, genres, yggtorrent_user, yggtorrent_password, yggtorrent_url)
    else:
        print("Le chemin spécifié n'est ni un dossier ni un fichier valide.")
    
if __name__ == '__main__':
    main()
