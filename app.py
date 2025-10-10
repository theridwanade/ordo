import os, re
import shutil
from pathlib import Path
import questionary


path = os.path

movies_source = questionary.path("What's the path to the movies").ask()
movies_subtitle_source = questionary.path("What's the path to the movies subtitle").ask()
movie_destination = questionary.path("What's the path to the destination").ask()

# "../../../../run/user/1000/gvfs/mtp:host=Unisoc_TECNO_POP_8_11002373CE003858/Internal shared storage/Android/data/com.community.oneroom/files/Download/d"
# "../../../../run/user/1000/gvfs/mtp:host=Unisoc_TECNO_POP_8_11002373CE003858/Internal shared storage/Android/data/com.community.oneroom/files/Download/subtitle/"
# "../../../../media/theridwanade/Ridwan/06_Archive/Movies/"


def get_movie_names():
    series_patterns = re.compile(
    r"^(?P<name>.+?)(?:_\d+p)?_S\d{1,2}_E\d{1,2}\.(mp4|avi|mkv|mov)$",
    re.IGNORECASE)
    movie_patterns = re.compile(
        r"^(?P<name>.+?)(?:_\d+p)?\.(mp4|avi|mkv|mov)$",
        re.IGNORECASE )
    movie_name = []
    movies_list = os.listdir(movies_source)
    for movie in movies_list:
        match = series_patterns.match(movie)
        if match:
            movie_name.append(match.group("name"))
        else:
            match = movie_patterns.match(movie)
            if match:
                movie_name.append(match.group("name"))
            else:
                print(f"Unrecognized file format: {movie_patterns}")
    return set(movie_name)

def get_movie_tags():
    movie_tag = []
    movies = list(get_movie_names())
    tags_list = [
                "Chinese archive",
                "American archive",
                "Korean archive",
                "Anime"
            ]
    # # print the tags formated
    for tag in tags_list:
        print(tag)

    for movie in movies:
        while True:
            tag_name = questionary.select(f"Select a tag for {movie}:", choices=[
                "Chinese archive",
                "American archive",
                "Korean archive",
                "Anime",
                "Ignore"
            ]).ask()
            if tag_name == "Ignore":
                break

            movie_tag.append({"movie": movie, "tag": tag_name})
            break

    return movie_tag



def copy_movies():
    movies_list = os.listdir(movies_source)
    for movie in movies_names:
        movie_file_names = [f for f in movies_list if f.startswith(movie["movie"])]
        for i in range(len(movie_file_names)):
            movie_file_path = movies_source + "/" + movie_file_names[i]
            destination = Path(movie_destination) /movie["tag"] / movie["movie"]
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(movie_file_path, destination)

def copy_subtitle():
    subtitle_folder_list = os.listdir(movies_subtitle_source)
    for movie in movies_names:
        for subtitle_folder in subtitle_folder_list:
            if subtitle_folder.startswith(movie["movie"]):
                for file_name in os.listdir(movies_subtitle_source + "/" + subtitle_folder):
                    subtitle_file_path = movies_subtitle_source + "/" + subtitle_folder + "/" + file_name
                    subtitle_destination = Path(movie_destination) / movie["tag"] / movie["movie"] / "subtitle"
                    subtitle_destination.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(subtitle_file_path, subtitle_destination)

    return

if __name__ == "__main__":
    movies_names = get_movie_tags()
    copy_movies()
    copy_subtitle()
