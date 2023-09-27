# Yggtorrent auto upload torrent

![YggTorrent logo](https://lh3.googleusercontent.com/vor06bIGjgTqtd5aZDykrD4tJcUFISFYOFYE5RYFmns6TstLs0_OkvcgHFUSnqoAKfKFTXwR5CaUjHVeUcCXcDWmzA=w128-h128-e365-rj-sc0x00ffffff "YggTorrent logo")
![Windows logo](https://files.softicons.com/download/system-icons/windows-8-metro-icons-by-dakirby309/png/128x128/Folders%20&%20OS/Windows.png "Windows logo")
![Linux logo](https://static-00.iconduck.com/assets.00/linux-icon-128x128-01vvcvmw.png "Linux logo")

Ce projet permet de mettre en ligne des torrents de manière automatisée sur YggTorrent, cela comprend :

- Renommage du fichier avec la bonne nomenclature yggtorrent (prends en compte les dossiers, saisons ou simple fichier en fonction du format audio et vidéo, la source, ...)
- Génération de la présentation
- Ajout des éléments dans la présentation via tmdb
- Récupération des informations du média via mediainfo
- Création du torrent
- Création du fichier NFO
- Création de l'upload en web
- ...

> Ce projet est un premier jet, il reste encore des fonctionnalités à développer. Certaines sont simples et d'autres demandes un peu plus de temps. Vous pouvez participer si vous le souhaitez. En cas d'aide vous pouvez ouvrir une issue GitHub.

## Installation

1. **Installer Python**: Si vous n'avez pas encore Python 3 installé, vous pouvez le télécharger à partir du [site officiel de Python](https://www.python.org/downloads/) et suivez les instructions d'installation pour votre système d'exploitation.

2. **Installer pip**: Si vous ne l'avez pas déjà, assurez-vous d'installer `pip`, le gestionnaire de paquets Python. Vous pouvez généralement le trouver inclus dans l'installation de Python.

3. **Télécharger le projet**: Vous pouvez cloner ce dépôt Git ou télécharger le code source sous forme de fichier ZIP.

4. **Installer les dépendances**: Naviguez vers le répertoire du projet et exécutez la commande suivante pour installer les dépendances à partir du fichier `requirements.txt` :

```python
pip install -r requirements.txt
```

5. **Création d'une clée api tmdb**: Rendez-vous sur ce site et enregistrez-vous : [Créer un compte TMDB](https://www.themoviedb.org/signup)

6. **Configurer les variables**: Ouvrez le fichier [init.py](init.py) et modifiez les variables suivantes selon vos besoins :

```python
tracker_url = "http://connect.drago-server.org:8080/xxxxxxxxxxxxxxxxxx/announce"
tmdb_api_key = ''
yggtorrent_user = ''
yggtorrent_password = ''
seeding_folder = r"Z:\Vidéos\Seeding"
torrent_folder = r"Z:\Vidéos\Seeding\0 - TORRENT FILES"
nfo_folder = r"Z:\Vidéos\Seeding\1 - NFO FILES"
root_path = r"Z:\Vidéos\Downloaded"
```

## Utilisation

Pour lancer le script, vous pouvez exécuter init.py à partir de votre terminal :

```
python init.py
```

Assurez-vous d'être dans le répertoire du projet lors de l'exécution du script.

### Pour Linux

Installer les packages :

- mediainfo
- chromium-chromedriver

```bash
sudo apt install mediainfo chromium-chromedriver
```

## Personnalisation

Il est possible d'avoir des templates pré-enregistrés pour faciliter la traduction sur les présentations. Pour cela il vous suffit d'adapter le fichier [titles.json](titles.json) à votre convenance.
