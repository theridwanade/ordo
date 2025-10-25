from setuptools import setup

setup(
    name="ordo",
    version="0.1.1",
    py_modules=["main"],
    install_requires=[
        "typer",
        "questionary", 
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "ordo = main:app",
        ],
    },
    author="theridwanade",
    author_email="theridwanade@gmail.com",
    license="MIT",
    description="A CLI tool to organize movie files into categorized folders.",
)
