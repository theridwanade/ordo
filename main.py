import json
import os, re
import shutil
from pathlib import Path
import questionary
from tqdm import tqdm
import typer

app = typer.Typer(help="An opinionated Python CLI for movie organization.")
path = os.path


def get_sources():
    last_sources_store = Path("sources.json")
    if last_sources_store.exists():
        with open("sources.json","r") as json_file:
            last_sources = json.load(json_file)
        use_last = questionary.confirm(
                f"Do you want to use the last sources?\nMovies: {last_sources['movies_source']}\nSubtitle: {last_sources['movies_subtitle_source']}\nDestination: {last_sources['movie_destination']}\n"
            ).ask()
        if use_last:
            return last_sources['movies_source'], last_sources['movies_subtitle_source'], last_sources['movie_destination']

    last_sources_store.touch(exist_ok=True)
    movies_source = questionary.path("What's the path to the movies").ask()
    movies_subtitle_source = questionary.path("What's the path to the movies subtitle").ask()
    movie_destination = questionary.path("What's the path to the destination").ask()
    with open("sources.json","w") as json_file:
        json.dump({
            "movies_source": movies_source,
            "movies_subtitle_source": movies_subtitle_source,
            "movie_destination": movie_destination
        }, json_file, indent=4)
    return movies_source, movies_subtitle_source, movie_destination

[movies_source, movies_subtitle_source, movie_destination] = get_sources()

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
                "Anime",
                "Ignore",
            ]

    for movie in movies:
        while True:
            tag_name = questionary.select(f"Select a tag for {movie}:", choices=tags_list).ask()
            if tag_name == "Ignore":
                break

            movie_tag.append({"movie": movie, "tag": tag_name})
            break

    return movie_tag

def copy_movies(movies_names):
    movies_list = os.listdir(movies_source)
    for movie_info in tqdm(movies_names, desc="Copying movie folders"):
        movie_file_names = [
            f for f in movies_list if f.startswith(movie_info["movie"])
        ]
        for movie_file in tqdm(movie_file_names, desc=f"{movie_info['movie']}", leave=False):
            movie_file_path = Path(movies_source) / movie_file
            destination = Path(movie_destination) / movie_info["tag"] / movie_info["movie"]
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(movie_file_path, destination)

def copy_subtitle(movies_names):
    subtitle_folder_list = os.listdir(movies_subtitle_source)
    for movie in tqdm(movies_names, desc="Copying subtitle folders"):
        for subtitle_folder in subtitle_folder_list:
            if subtitle_folder.startswith(movie["movie"]):
                for file_name in tqdm(os.listdir(movies_subtitle_source + "/" + subtitle_folder), desc=f"{movie['movie']}", leave=False):
                    subtitle_file_path = movies_subtitle_source + "/" + subtitle_folder + "/" + file_name
                    subtitle_destination = Path(movie_destination) / movie["tag"] / movie["movie"] / "subtitle"
                    subtitle_destination.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(subtitle_file_path, subtitle_destination)

    return


@app.command()
def organize():
    movies_names = get_movie_names()
    copy_movies(movies_names)
    copy_subtitle(movies_names)


@app.command()
def help():
    """Display help information about the CLI commands."""
    typer.echo(f"Here is help")



def main():
    """Main function to run the movie organization CLI."""
    app()


if __name__ == "__main__":
    main()
