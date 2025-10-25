from setuptools import setup, find_packages

setup(
    name="ordo",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "questionary", 
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "ordo = ordo.cli.main:main",
        ],
    },
    python_requires=">=3.8",
    author="theridwanade",
    author_email="theridwanade@gmail.com",
    license="MIT",
    description="An opinionated Python CLI for movie organization",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
