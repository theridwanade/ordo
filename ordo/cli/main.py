import typer
import time
import logging
from typing import Optional
from pathlib import Path
from ..services.organization import MovieOrganizer

# ✅ COMPLETED: Modularized the project code into organized packages
# TODO: Handle movies with multiple seasons
# ✅ COMPLETED: Add concurrency and multi-threading
# ✅ COMPLETED: Handle metadata for movies
# ✅ COMPLETED: Implement files moving, and copying options
# ✅ COMPLETED: Handle checksums creation for file verification
# ✅ COMPLETED: Manage file chunk, streaming and operation resumption.
# ✅ COMPLETED: Implement logging, progress tracking and improved UX


# Configure logging
def setup_logging(log_file: Optional[Path] = None, verbose: bool = False):
    """Configure logging for the application."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log file specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)


app = typer.Typer(help="An opinionated Python CLI for movie organization.")

@app.command()
def organize(
    log_file: Optional[str] = typer.Option(None, "--log-file", "-l", help="Log file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    legacy: bool = typer.Option(False, "--legacy", help="Use legacy file operations (copy only)")
):
    """Organize movies into categorized folders."""
    # Setup logging
    log_path = Path(log_file) if log_file else None
    setup_logging(log_path, verbose)
    
    organizer = MovieOrganizer(use_enhanced_operations=not legacy)
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
