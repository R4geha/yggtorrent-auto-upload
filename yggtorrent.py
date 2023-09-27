from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time, re, os, requests



def init(destination_path, bbcode_description, new_title_without_format, chosen_category, nfo_output_path, destination_torrent_path, genres, yggtorrent_user, yggtorrent_password, yggtorrent_url):
    response = requests.get('http://httpbin.org/headers')

    header=response.text

    # Chemin vers le chromedriver (téléchargez-en un compatible avec votre version de Chrome)
    if os.name == 'nt':
        path = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(path, 'chromedriver.exe')
    else:
        chromedriver_path = "/usr/lib/chromium-browser/chromedriver" # Si vous êtes sur Linux/Mac

    # Configuration du navigateur
    options = webdriver.ChromeOptions()
    # options.add_argument('--disable-extensions')
    # options.add_argument(r"--user-data-dir=C:\Users\test\AppData\Local\Google\Chrome\User Data\Default")
    options.add_argument(f'user-agent={header}')
    #options.add_argument('--headless')  # Exécuter Chrome en mode headless (sans interface graphique)

    # Initialisation du navigateur Chrome
    driver = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=options)

    # Accéder à la page de connexion
    driver.get(yggtorrent_url)
    time.sleep(2)

    # Suppression des cookies
    driver.delete_all_cookies()

    login(yggtorrent_user, yggtorrent_password, driver)
    upload_torrent(driver)
    category_selecting(driver, chosen_category)
    upload_files(driver, nfo_output_path, destination_torrent_path)
    torrent_name_desc(driver, bbcode_description, new_title_without_format)
    if chosen_category in [2, 5, 7]:
        episode_field(driver, new_title_without_format)
        season_field(driver, new_title_without_format)
        language_field_serie(driver, new_title_without_format)
        quality_field_serie(driver, new_title_without_format)
        system_field_serie(driver)
        type_field_serie(driver)
        kind_field_serie(driver, genres)
    elif chosen_category in [1, 4, 6, 8]:
        language_field_movie(driver, new_title_without_format)
        quality_field_movie(driver, new_title_without_format)
        system_field_movie(driver)
        type_field_movie(driver)
        kind_field_movie(driver, genres)
    time.sleep(600)
    
    # Fermer le navigateur
    driver.quit()

def login(yggtorrent_user, yggtorrent_password, driver):
    driver.find_element("xpath", '/html/body/div[4]/div[1]/ul/li[1]/a').click()
    time.sleep(1)
    driver.find_element("xpath", '/html/body/div[2]/form/input[1]').click()
    yggtorrent_user_field = driver.find_element("xpath", '/html/body/div[2]/form/input[1]')
    time.sleep(0.5)
    yggtorrent_user_field.send_keys(yggtorrent_user)
    time.sleep(0.5)
    driver.find_element("xpath", '/html/body/div[2]/form/input[2]').click()
    password_field = driver.find_element("xpath", '/html/body/div[2]/form/input[2]')
    time.sleep(0.5)
    password_field.send_keys(yggtorrent_password)
    time.sleep(0.5)
    login_button = driver.find_element("xpath", '/html/body/div[2]/form/button').click()
    time.sleep(2)

def upload_torrent(driver):
    driver.find_element("xpath", '/html/body/div[5]/div/nav/ul/li[3]/a').click()
    time.sleep(0.5)
    driver.find_element("xpath", '/html/body/div[5]/div/nav/ul/li[3]/ul/li[7]/a').click()

def category_selecting(driver, chosen_category): 
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[1]/div[2]/div/div/select').click()
    driver.find_element("xpath", '//*[@id="upload-torrent"]/div/div[1]/div[2]/div/div/select/option[2]').click()
    # Select Sub-Category
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[2]/div[2]/div/div/select[1]').click()
    driver.find_element("xpath", f'/html/body/div[9]/main/div/div/section[2]/form/div/div[2]/div[2]/div/div/select[1]/option[{chosen_category}]').click()

def upload_files(driver, nfo_output_path, destination_torrent_path):
    # Upload File Torrent
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[3]/div[2]/div/div/input').send_keys(destination_torrent_path)
    # Upload NFO
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[4]/div[2]/div/div/input').send_keys(nfo_output_path)

def torrent_name_desc(driver, bbcode_description, new_title_without_format):
    #Torrent Name
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[5]/div[2]/div/div/input').click()
    torrent_name_field = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[5]/div[2]/div/div/input')
    torrent_name_field.send_keys(new_title_without_format)

    #Torrent Description
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[6]/div[2]/div/div/div/div[1]/div[7]/div/span').click()
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[6]/div[2]/div/div/div/div[2]/textarea').click()
    description_field = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[6]/div[2]/div/div/div/div[2]/textarea')
    description_field.send_keys(bbcode_description)

def episode_field(driver, new_title_without_format):
    ### FOR ANIMATION SERIE/ TV SERIE / TV SHOW
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[1]/div[2]/div/div/span/span[1]/span/span[1]').click()
    episode_element = driver.find_element("xpath", '/html/body/span/span/span[1]/input')
    episode_element.click()
    episode_match = re.search(r'E(\d+)', new_title_without_format)
    if episode_match:
        episode_number = int(episode_match.group(1))
        formatted_episode = f"Episode {episode_number:02}"
    else:
        formatted_episode = " Saison complète"
    episode_element.send_keys(formatted_episode)
    episode_element.send_keys(Keys.RETURN)

def season_field(driver, new_title_without_format):
    ### FOR ANIMATION SERIE/ TV SERIE / TV SHOW
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[2]/div[2]/div/div/span/span[1]/span/span[1]').click()
    season_element = driver.find_element("xpath", '/html/body/span/span/span[1]/input')
    season_element.click()
    season_match = re.search(r'.S0(\d{1,2})|.S(\d{1,2})', new_title_without_format)
    if season_match:
        season_number = int(season_match.group(1) or season_match.group(2))
        formatted_season = f"Saison {season_number:02}"
    season_element.send_keys(formatted_season)
    season_element.send_keys(Keys.RETURN)
    
def language_field_serie(driver, new_title_without_format):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[3]/div[2]/div/div/span/span[1]/span/ul/li/input').click()
    language_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[3]/div[2]/div/div/span/span[1]/span/ul/li/input')
    if "VFF." in new_title_without_format:
        language_value = "Français (VFF/Truefrench)"
    elif "FRENCH." in new_title_without_format:
        language_value = "Français (VFF/Truefrench)"
    elif "MULTI." in new_title_without_format:
        language_value = "Multi (Français inclus)"
    elif "VOSTFR." in new_title_without_format:
        language_value = "VOSTFR"
    language_element.send_keys(language_value)
    language_element.send_keys(Keys.RETURN)

def quality_field_serie(driver, new_title_without_format):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[4]/div[2]/div/div/span/span[1]/span/span[1]').click()
    quality_element = driver.find_element("xpath", '/html/body/span/span/span[1]/input')
    quality_element.click()
    if ".1080p." in new_title_without_format:
        quality_value = "Web-Dl 1080"
    elif ".720p." in new_title_without_format:
        quality_value = "Web-Dl 720"
    elif ".2160p." in new_title_without_format:
        quality_value = "Web-Dl 2160"
    quality_element.send_keys(quality_value)
    quality_element.send_keys(Keys.RETURN)
    quality_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[4]/div[2]/div/div/span/span[1]/span/span[1]')
    driver.execute_script("arguments[0].innerText = arguments[1];", quality_element, quality_value)
    driver.execute_script("arguments[0].setAttribute('title', arguments[1]);", quality_element, quality_value)

def system_field_serie(driver):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[5]/div[2]/div/div/span/span[1]/span/ul/li/input').click()
    system_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[5]/div[2]/div/div/span/span[1]/span/ul/li/input')
    system_element_list = "PC/Platine/Lecteur Multimédia/etc"
    system_element.send_keys(system_element_list)
    system_element.send_keys(Keys.RETURN)

def type_field_serie(driver):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[6]/div[2]/div/div/span/span[1]/span/span[1]').click()
    system_element = driver.find_element("xpath", '/html/body/span/span/span[1]/input')
    system_element.click()
    system_element_list = "2D (Standard)"
    system_element.send_keys(system_element_list)
    system_element.send_keys(Keys.RETURN)

def kind_field_serie(driver, genres):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[7]/div[2]/div/div/span/span[1]/span/ul/li/input').click()
    kind_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[7]/div[2]/div/div/span/span[1]/span/ul/li/input')
    genres_YGG = ['Action', 'Animalier', 'Animation', 'Aventure', 'Documentaire', 'Comédie', 'Divers', 'Drame', 'Enquête', 'Epouvante & Horreur', 'Famille', 'Fantastique', 'Fiction', 'Guerre', 'Historique', 'Policier', 'Romance', 'Science fiction', 'Humour', 'Thriller', 'Sciences & Technologies', 'Télé-Réalité', 'Western']
    nouvelle_liste = []
    for element in genres:
        if element in genres_YGG:
            nouvelle_liste.append(element)
        elif element == "Action & Adventure" and "Action" in genres_YGG:
            nouvelle_liste.append("Action")
            nouvelle_liste.append("Aventure")
        elif element == "Familial" and "Famille" in genres_YGG:
            nouvelle_liste.append("Famille")
        elif element == "Horreur" and "Epouvante & Horreur" in genres_YGG:
            nouvelle_liste.append("Epouvante & Horreur")
        elif element == "Reality" and "Télé-Réalité" in genres_YGG:
            nouvelle_liste.append("Télé-Réalité")
        elif element == "Science-Fiction & Fantastique" and "Science fiction" in genres_YGG:
            nouvelle_liste.append("Science fiction")
            nouvelle_liste.append("Fantastique")
        elif element == "War & Politics" and "Guerre" in genres_YGG:
            nouvelle_liste.append("Guerre")
    for i in nouvelle_liste:
        kind_element.send_keys(i)
        kind_element.send_keys(Keys.RETURN)

def language_field_movie(driver, new_title_without_format):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[1]/div[2]/div/div/span/span[1]/span/ul/li/input').click()
    language_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[1]/div[2]/div/div/span/span[1]/span/ul/li/input')
    if "VFF." in new_title_without_format:
        language_value = "Français (VFF/Truefrench)"
    elif "MULTI." in new_title_without_format:
        language_value = "Multi (Français inclus)"
    elif "VOSTFR." in new_title_without_format:
        language_value = "VOSTFR"
    language_element.send_keys(language_value)
    language_element.send_keys(Keys.RETURN)

def quality_field_movie(driver, new_title_without_format):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[2]/div[2]/div/div/span/span[1]/span/span[1]').click()
    quality_element = driver.find_element("xpath", '/html/body/span/span/span[1]/input')
    quality_element.click()
    if ".1080p." in new_title_without_format:
        quality_value = "Web-Dl 1080"
    elif ".720p." in new_title_without_format:
        quality_value = "Web-Dl 720"
    elif ".2160p." in new_title_without_format:
        quality_value = "Web-Dl 2160"
    quality_element.send_keys(quality_value)
    quality_element.send_keys(Keys.RETURN)
    quality_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[2]/div[2]/div/div/span/span[1]/span/span[1]')
    driver.execute_script("arguments[0].innerText = arguments[1];", quality_element, quality_value)
    driver.execute_script("arguments[0].setAttribute('title', arguments[1]);", quality_element, quality_value)

def system_field_movie(driver):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[3]/div[2]/div/div/span/span[1]/span/ul/li/input').click()
    system_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[3]/div[2]/div/div/span/span[1]/span/ul/li/input')
    system_element_list = "PC/Platine/Lecteur Multimédia/etc"
    system_element.send_keys(system_element_list)
    system_element.send_keys(Keys.RETURN)

def type_field_movie(driver):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[4]/div[2]/div/div/span/span[1]/span/span[1]').click()
    system_element = driver.find_element("xpath", '/html/body/span/span/span[1]/input')
    system_element.click()
    system_element_list = "2D (Standard)"
    system_element.send_keys(system_element_list)
    system_element.send_keys(Keys.RETURN)

def kind_field_movie(driver, genres):
    driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[5]/div[2]/div/div/span/span[1]/span/ul/li/input').click()
    kind_element = driver.find_element("xpath", '/html/body/div[9]/main/div/div/section[2]/form/div/div[8]/div[5]/div[2]/div/div/span/span[1]/span/ul/li/input')
    genres_YGG = ['Action', 'Animalier', 'Animation', 'Aventure', 'Documentaire', 'Comédie', 'Divers', 'Drame', 'Enquête', 'Epouvante & Horreur', 'Famille', 'Fantastique', 'Fiction', 'Guerre', 'Historique', 'Policier', 'Romance', 'Science fiction', 'Humour', 'Thriller', 'Sciences & Technologies', 'Télé-Réalité', 'Western']
    nouvelle_liste = []
    for element in genres:
        if element in genres_YGG:
            nouvelle_liste.append(element)
        elif element == "Familial" and "Famille" in genres_YGG:
            nouvelle_liste.append("Famille")
        elif element == "Histoire" and "Historique" in genres_YGG:
            nouvelle_liste.append("Historique")
        elif element == "Horreur" and "Epouvante & Horreur" in genres_YGG:
            nouvelle_liste.append("Epouvante & Horreur")
        elif element == "Science-Fiction" and "Science fiction" in genres_YGG:
            nouvelle_liste.append("Science fiction")  
    for i in nouvelle_liste:
        kind_element.send_keys(i)
        kind_element.send_keys(Keys.RETURN)
