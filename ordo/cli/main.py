import typer
import time
from typing import Optional
from ..services.organization import MovieOrganizer

# ✅ COMPLETED: Modularized the project code into organized packages
# TODO: Handle movies with multiple seasons
# TODO: Add concurrency and multi-threading  
# TODO: Handle metadata for movies
# TODO: Implement files moving, and copying options
# TODO: Handle checksums creation for file verification
# TODO: Manage file chunk, streaming and operation resumption.
# TODO: Implement logging, progress tracking and improved UX


app = typer.Typer(help="An opinionated Python CLI for movie organization.")

@app.command()
def organize():
    """Organize movies into categorized folders."""
    organizer = MovieOrganizer()
    try:
        organizer.organize_movies()
    except KeyboardInterrupt:
        typer.echo("\nOperation cancelled by user")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def greet(name: str):
    """Greet someone by name."""
    typer.echo(f"Hello, {name}!")

@app.command() 
def sleep(seconds: int = typer.Argument(..., help="Number of seconds to sleep")):
    """Sleep for specified number of seconds."""
    time.sleep(seconds)
    typer.echo(f"Slept for {seconds} seconds.")

@app.command()
def version():
    """Show version information."""
    from .. import __version__
    typer.echo(f"Ordo version {__version__}")

def main():
    """Main CLI entry point."""
    app()

if __name__ == "__main__":
    main()
