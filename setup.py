"""
Setup configuration for Clipr
"""

from setuptools import setup, find_packages
from pathlib import Path

# Ler README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="clipr",
    version="1.0.0",
    author="Felipe Cavalari",
    description="Ferramenta CLI para download de vídeos do YouTube e Instagram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CavalariDev/clipr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "yt-dlp>=2024.0.0",
        "rich>=13.0.0",
        "openai-whisper>=20230314",
        "pydub>=0.25.1",
    ],
    entry_points={
        "console_scripts": [
            "clipr=clipr.cli:main",
        ],
    },
    keywords="youtube instagram download video reels shorts cli",
)
