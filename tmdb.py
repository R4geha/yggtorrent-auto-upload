import requests, re, locale, os
from datetime import datetime
from unidecode import unidecode

BASE_URL = 'https://api.themoviedb.org/3'
SEARCH_MOVIE_ENDPOINT = '/search/movie'
SEARCH_TV_ENDPOINT = '/search/tv'
DETAILS_ENDPOINT = '/movie/{}?language=fr-FR'
DETAILS_ENDPOINT_EN = '/movie/{}'
DETAILS_TV_ENDPOINT = '/tv/{}?language=fr-FR'
DETAILS_TV_ENDPOINT_EN = '/tv/{}'
TV_EPISODES_ENDPOINT = '/tv/{}/season/{}/episode/{}?language=fr-FR'

def search_movies(query, tmdb_api_key):
    params = {
        'api_key': tmdb_api_key,
        'query': query
    }
    response = requests.get(BASE_URL + SEARCH_MOVIE_ENDPOINT, params=params)
    data = response.json()
    results = data.get('results', [])
    return results

def search_series(query, tmdb_api_key):
    params = {
        'api_key': tmdb_api_key,
        'query': query
    }
    response = requests.get(BASE_URL + SEARCH_TV_ENDPOINT, params=params)
    data = response.json()
    results = data.get('results', [])
    return results

def get_item_details(item_id, tmdb_api_key, is_movie=True):
    endpoint = DETAILS_ENDPOINT.format(item_id) if is_movie else DETAILS_TV_ENDPOINT.format(item_id)
    params = {
        'api_key': tmdb_api_key
    }
    response = requests.get(BASE_URL + endpoint, params=params)
    details = response.json()
    return details

def get_item_title(item_id, tmdb_api_key, is_movie=True):
    endpoint = DETAILS_ENDPOINT_EN.format(item_id) if is_movie else DETAILS_TV_ENDPOINT_EN.format(item_id)
    params = {
        'api_key': tmdb_api_key
    }
    response = requests.get(BASE_URL + endpoint, params=params)
    details_en = response.json()
    return details_en

def get_tv_episode_details(series_id, season_number, episode_number, tmdb_api_key):
    endpoint = TV_EPISODES_ENDPOINT.format(series_id, season_number, episode_number)
    params = {
        'api_key': tmdb_api_key
    }
    response = requests.get(BASE_URL + endpoint, params=params)
    details = response.json()
    return details

def format_datetime_to_french(date_time):
    mois_fr = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
        7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }
    jours_semaine_fr = {
        'Monday': "lundi", 'Tuesday': "mardi", 'Wednesday': "mercredi", 'Thursday': "jeudi",
        'Friday': "vendredi", 'Saturday': "samedi", 'Sunday': "dimanche"
    }

    jour_semaine = jours_semaine_fr[date_time.strftime('%A')]
    jour = date_time.day
    mois = mois_fr[date_time.month]
    annee = date_time.year
    
    formatted_date = f"{jour_semaine} {jour} {mois} {annee}"
    return formatted_date

def generate_bbcode_for_movie(details, tmdb_api_key, data_titles):
    title_key = 'title'
    original_title_key = 'original_title'

    found = False
    for title_info in data_titles["titles"]:
        if title_info["name"] == details[title_key] or title_info["name"] == details[original_title_key]:
            found = True
            json_title_name = title_info["new_title"]
            json_original_title = title_info["original_title"]
            json_title_description = title_info["description"]
    if not found:
        print("Title non trouvé dans le JSON.")
        
    tmdb_url = f"https://www.themoviedb.org/movie/{details['id']}"
    if found == True:
        bbcode = f"[center][size=200][color=#aa0000][b]{json_title_name} ({details.get('release_date', '').split('-')[0]})[/b][/color][/size]\n"
    else:
        bbcode = f"[center][size=200][color=#aa0000][b]{details[title_key]} ({details.get('release_date', '').split('-')[0]})[/b][/color][/size]\n"
    bbcode += f"[img]https://image.tmdb.org/t/p/w500/{details['poster_path']}[/img]\n\n"
    bbcode += f"\n\n[img]https://i.imgur.com/oiqE1Xi.png[/img]\n\n"
    movie_details_endpoint = f"/movie/{details['id']}?language=fr-FR&append_to_response=credits,production_countries"
    movie_details_response = requests.get(BASE_URL + movie_details_endpoint, params={'api_key': tmdb_api_key})
    movie_details = movie_details_response.json()
    bbcode += f"[b]Origine :[/b] {', '.join(country['name'] for country in movie_details.get('production_countries', []))}\n"
    formatted_release_date = "N/A"
    release_date = details.get('release_date')
    if release_date:
        release_datetime = datetime.strptime(release_date, '%Y-%m-%d')
        formatted_release_date = format_datetime_to_french(release_datetime)
    bbcode += f"[b]Sortie :[/b] {formatted_release_date}\n"
    if found == True:
        bbcode += f"[b]Titre original :[/b] {json_original_title}\n"
    else:
        bbcode += f"[b]Titre original :[/b] {details[original_title_key]}\n"
    duration_minutes = movie_details.get('runtime', 0)
    hours = duration_minutes // 60
    minutes = duration_minutes % 60
    bbcode += f"[b]Durée :[/b] {hours}h {minutes}min\n\n"
    bbcode += f"[b]Réalisateur(s) :[/b] "
    directors = [director['name'] for director in movie_details.get('credits', {}).get('crew', []) if director['job'] == 'Director']
    bbcode += ", ".join(directors) + "\n\n"
    bbcode += f"[b]Acteurs :[/b]\n"
    actor_names = []
    for index, actor in enumerate(movie_details.get('credits', {}).get('cast', []), start=1):
        if index > 4:  # Limiter à 4 acteurs
            break
        actor_name = actor.get('name', 'N/A')
        actor_character = actor.get('character', 'N/A')
        actor_profile_path = actor.get('profile_path')
        if actor_profile_path:
            actor_photo = f"https://image.tmdb.org/t/p/w138_and_h175_face/{actor_profile_path}"
            bbcode += f"[img]{actor_photo}[/img] "
            actor_names.append(actor_name)
        else:
            actor_names.append(actor_name)
    if actor_names:
        bbcode += "\n"
        bbcode += ', '.join(actor_names)
    bbcode += "\n\n"
    bbcode += f"[b]Genres :[/b]\n"
    genres = [genre['name'] for genre in movie_details.get('genres', [])]
    bbcode += ", ".join(genres) + "\n\n"
    bbcode += f"[b]Note :[/b] {round(details.get('vote_average', '0'),1)}/10\n\n"
    bbcode += f"[img]https://zupimages.net/up/21/03/mxao.png[/img] [url={tmdb_url}]Fiche du film[/url]\n\n"
    bbcode += f"\n\n[img]https://i.imgur.com/HS8PPgH.png[/img]\n\n"
    if 'overview' in details and details['overview']:
        bbcode += f"{details['overview']}\n\n"
    else:
        if found == True:
            bbcode += f"{json_title_description}\n\n"
        else:
            bbcode += f"Aucun résumé disponible. \n\n"
    return bbcode, genres


def generate_bbcode_for_series(details, casts, season_number, episode_number, isFolder, data_titles, episode_details=None):
    title_key = 'name'
    original_title_key = 'original_name'
    print(details[title_key] + "\n")
    print(details[original_title_key])

    found = False
    for title_info in data_titles["titles"]:
        if title_info["name"] == details[title_key] or title_info["name"] == details[original_title_key]:
            found = True
            json_title_name = title_info["new_title"]
            json_original_title = title_info["original_title"]
            json_title_description = title_info["description"]
    if not found:
        print("Title non trouvé dans le JSON.")

    tmdb_url = f"https://www.themoviedb.org/tv/{details['id']}"
    if found == True:
        bbcode = f"[center][size=200][color=#aa0000][b]{json_title_name} ({details.get('first_air_date', '').split('-')[0]})[/b][/color][/size]\n"
    else:
        bbcode = f"[center][size=200][color=#aa0000][b]{details[title_key]} ({details.get('first_air_date', '').split('-')[0]})[/b][/color][/size]\n"
    if isFolder == "folder":
        bbcode += f"[size=200][color=#aa0000][b]S{season_number:02}[/b][/color][/size]\n"
    else:
        bbcode += f"[size=200][color=#aa0000][b]S{season_number:02}E{episode_number:02}[/b][/color][/size]\n"
    bbcode += f"[img]https://image.tmdb.org/t/p/w500/{details['poster_path']}[/img]\n\n"
    bbcode += f"\n\n[img]https://i.imgur.com/oiqE1Xi.png[/img]\n\n"
    bbcode += f"[b]Origine :[/b] {', '.join(details.get('origin_country', []))}\n"
    formatted_first_air_date = "N/A"
    first_air_date = details.get('first_air_date')
    if first_air_date:
        first_air_datetime = datetime.strptime(first_air_date, '%Y-%m-%d')
        formatted_first_air_date = format_datetime_to_french(first_air_datetime)
    bbcode += f"[b]Première diffusion :[/b] {formatted_first_air_date}\n"
    if found == True:
        bbcode += f"[b]Titre original :[/b] {json_original_title}\n\n"
    else:
        bbcode += f"[b]Titre original :[/b] {details[original_title_key]}\n\n"
    if episode_details:
        bbcode += f"[b]Durée :[/b] {episode_details.get('runtime', 'N/A')} minutes\n\n"
    creators_and_directors = []
    creators_and_directors.extend([creator['name'] for creator in details.get('created_by', [])])
    if episode_details:
        directors = [director['name'] for director in episode_details.get('crew', []) if director['job'] == 'Director']
        creators_and_directors.extend(directors)
    bbcode += f"[b]Réalisateur(s) :[/b] {', '.join(creators_and_directors)}\n\n"
    if casts:
        bbcode += f"[b]Acteurs :[/b]\n"
        actor_names = []
        for index, actor in enumerate(casts.get('cast', []), start=1):
            if index > 4:  # Limiter à 4 acteurs
                break
            actor_name = actor.get('name', 'N/A')
            actor_character = actor.get('character', 'N/A')
            actor_profile_path = actor.get('profile_path')
            if actor_profile_path:
                actor_photo = f"https://image.tmdb.org/t/p/w138_and_h175_face/{actor_profile_path}"
                bbcode += f"[img]{actor_photo}[/img] "
                actor_names.append(actor_name)
            else:
                actor_names.append(actor_name)
        if actor_names:
            bbcode += "\n"
            bbcode += ', '.join(actor_names)
    bbcode += "\n\n"
    bbcode += f"[b]Genres :[/b]\n"
    genres = [genre['name'] for genre in details.get('genres', [])]
    bbcode += ", ".join(genres) + "\n\n"
    bbcode += f"[b]Note :[/b] {round(details.get('vote_average', '0'),1)}/10\n\n"
    bbcode += f"[img]https://zupimages.net/up/21/03/mxao.png[/img] [url={tmdb_url}]Fiche de la série[/url]\n\n"
    bbcode += f"\n\n[img]https://i.imgur.com/HS8PPgH.png[/img]\n\n"
    if 'overview' in details and details['overview']:
        bbcode += f"{details['overview']}\n\n"
    else:
        if found == True:
            bbcode += f"{json_title_description}\n\n"
        else:
            bbcode += f"Aucun résumé disponible. \n\n"    
    return bbcode, genres

def get_aggregate_credits(item_id, tmdb_api_key, is_movie=True):
    params = {
        'api_key': tmdb_api_key
    }
    item_type ='tv'
    response = requests.get(BASE_URL + f"/{item_type}/{item_id}/aggregate_credits", params=params)
    data = response.json()
    return data

def clean_title(title):
    cleaned_title = unidecode(title)
    cleaned_title = re.sub(r'[^a-zA-Z0-9]+', '.', cleaned_title)
    cleaned_title = re.sub(r'\.{2,}', '.', cleaned_title)
    cleaned_title = re.sub(r'^\.', '', cleaned_title)
    cleaned_title = re.sub(r'\.$', '', cleaned_title)
    return cleaned_title

def confirm_title(details, original_title, movie):
    print('#'*100)
    if movie == True:
        new_title = f"{clean_title(details['title'])}"
    else:
        new_title = f"{clean_title(details['original_name'])}"
    print(f"Titre actuel : {new_title} | Sinon : {clean_title(original_title)}")
    confirm_title_name = input(f"Voulez-vous garder ce titre ? [Oui/Non]")
    print('#'*100)
    if confirm_title_name.lower() in ["oui", "yes", "y", "o"]:
        return new_title
    else:
        new_title = f"{clean_title(original_title)}"
        return new_title    
    
def main(isFolder, tmdb_api_key, data_titles):
    query = input("Entrez le nom d'un film ou d'une série : ")
    movie_results = search_movies(query, tmdb_api_key)
    series_results = search_series(query, tmdb_api_key)
    
    if not movie_results and not series_results:
        print("Aucun résultat trouvé.")
        return
    
    print("Résultats pour les films :")
    for index, result in enumerate(movie_results, start=1):
        title = result.get('title', 'N/A')
        date = datetime.strptime(result.get('release_date', 'N/A'), "%Y-%m-%d").strftime("%d-%m-%Y") if result.get('release_date', 'N/A') else ""
        movie_link = f"https://www.themoviedb.org/movie/{result['id']}"
        print(f"{index}. Film : {title} [{date}] [{movie_link}]")
    
    print("\nRésultats pour les séries :")
    for index, result in enumerate(series_results, start=len(movie_results) + 1):
        title = result.get('name', 'N/A')
        date = datetime.strptime(result.get('first_air_date', 'N/A'), "%Y-%m-%d").strftime("%d-%m-%Y") if result.get('first_air_date', 'N/A') else ""
        series_link = f"https://www.themoviedb.org/tv/{result['id']}"
        print(f"{index}. Série : {title} [{date}] [{series_link}]")
    
    choice = int(input("Choisissez un film ou une série en entrant son numéro : "))
    
    if 1 <= choice <= len(movie_results) + len(series_results):
        if choice <= len(movie_results):
            selected_item = movie_results[choice - 1]
            item_id = selected_item['id']
            details = get_item_details(item_id, tmdb_api_key)
            details_en = get_item_title(item_id, tmdb_api_key)
            bbcode, genres = generate_bbcode_for_movie(details, tmdb_api_key, data_titles)
            if 'title' in details:
                new_title = f"{confirm_title(details, details_en['title'], movie=True)}.{details.get('release_date', '').split('-')[0]}."
            else:
                new_title = input("Titre original non disponible dans les détails. Mettez le votre avec les . et la date :")
            return bbcode, new_title, genres
        else:
            selected_item = series_results[choice - len(movie_results) - 1]
            item_id = selected_item['id']
            details = get_item_details(item_id, tmdb_api_key, is_movie=False)
            details_en = get_item_title(item_id, tmdb_api_key, is_movie=False)
            series_id = details['id']
            seasons = details.get('seasons', [])
            casts = get_aggregate_credits(item_id, tmdb_api_key, is_movie=False)
            print("\nSaisons et épisodes disponibles :")
            for season in seasons:
                season_number = season['season_number']
                episodes = season.get('episode_count', 0)
                print(f"\n------------------")
                for episode_number in range(1, episodes + 1):
                    print(f"S{season_number}E{episode_number} | ", end='')
            season_choice = int(input("\nChoisissez le numéro de la saison : "))
            episode_choice = int(input("Choisissez le numéro de l'épisode : "))
            selected_season = seasons[season_choice - 1]
            episode_number = episode_choice
            season_number = selected_season['season_number']
            episode_details = get_tv_episode_details(series_id, season_number, episode_number, tmdb_api_key)
            bbcode, genres = generate_bbcode_for_series(details, casts, season_number, episode_number, isFolder, data_titles, episode_details)
            if 'original_name' in details:
                if isFolder == "folder":
                    new_title = f"{confirm_title(details, details_en['name'], movie=False)}.{details.get('first_air_date', '').split('-')[0]}.S{season_number:02}."
                else:
                    new_title = f"{confirm_title(details, details_en['name'], movie=False)}.{details.get('first_air_date', '').split('-')[0]}.S{season_number:02}E{episode_number:02}."
            else:
                new_title = input("Titre original non disponible dans les détails. Mettez le votre avec les . et la date :")
            return bbcode, new_title, genres
    else:
        print("Choix invalide.")
        
if __name__ == '__main__':
    main()
