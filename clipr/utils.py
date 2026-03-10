"""
Módulo de utilitários para paths, validações e helpers
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


class VideoPath:
    """Gerenciador de caminhos para organização de vídeos"""
    
    @staticmethod
    def _get_videos_dir() -> Path:
        """Resolve o diretório de vídeos do sistema operacional."""
        home = Path.home()

        if sys.platform.startswith("win"):
            return home / "Videos"

        # Tenta ler XDG_VIDEOS_DIR (Linux e alguns ambientes)
        xdg_config = home / ".config" / "user-dirs.dirs"
        if xdg_config.exists():
            try:
                content = xdg_config.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    if line.startswith("XDG_VIDEOS_DIR="):
                        value = line.split("=", 1)[1].strip().strip('"')
                        value = value.replace("$HOME", str(home))
                        value = os.path.expandvars(value)
                        return Path(value)
            except Exception:
                pass

        # Fallbacks por plataforma
        if sys.platform == "darwin":
            return (home / "Movies") if (home / "Movies").exists() else (home / "Videos")

        return (home / "Videos") if (home / "Videos").exists() else (home / "Movies")

    BASE_PATH = _get_videos_dir.__func__() / "Videos baixados"
    YOUTUBE_PATH = BASE_PATH / "Youtube"
    INSTAGRAM_PATH = BASE_PATH / "Instagram"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Cria os diretórios necessários caso não existam"""
        cls.BASE_PATH.mkdir(parents=True, exist_ok=True)
        cls.YOUTUBE_PATH.mkdir(parents=True, exist_ok=True)
        cls.INSTAGRAM_PATH.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_output_path(cls, platform: str) -> Path:
        """Retorna o caminho de saída baseado na plataforma"""
        if platform.lower() == "youtube":
            return cls.YOUTUBE_PATH
        elif platform.lower() == "instagram":
            return cls.INSTAGRAM_PATH
        else:
            raise ValueError(f"Plataforma desconhecida: {platform}")


class URLValidator:
    """Validador e identificador de URLs de vídeos"""
    
    # Padrões de URL para YouTube
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
        r'(?:https?://)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
    ]
    
    # Padrões de URL para Instagram
    INSTAGRAM_PATTERNS = [
        r'(?:https?://)?(?:www\.)?instagram\.com/reel/[\w-]+',
        r'(?:https?://)?(?:www\.)?instagram\.com/p/[\w-]+',
        r'(?:https?://)?(?:www\.)?instagram\.com/tv/[\w-]+',
    ]
    
    @classmethod
    def identify_platform(cls, url: str) -> Optional[str]:
        """
        Identifica a plataforma baseada na URL
        
        Args:
            url: URL do vídeo
            
        Returns:
            'youtube', 'instagram' ou None se não identificado
        """
        url = url.strip()
        
        # Verifica YouTube
        for pattern in cls.YOUTUBE_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return "youtube"
        
        # Verifica Instagram
        for pattern in cls.INSTAGRAM_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return "instagram"
        
        return None
    
    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """Verifica se a URL é válida"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @classmethod
    def validate_and_identify(cls, url: str) -> tuple[bool, Optional[str]]:
        """
        Valida URL e identifica a plataforma
        
        Returns:
            (is_valid, platform)
        """
        if not cls.is_valid_url(url):
            return False, None
        
        platform = cls.identify_platform(url)
        return platform is not None, platform


def sanitize_filename(filename: str) -> str:
    """
    Remove caracteres inválidos do nome do arquivo
    
    Args:
        filename: Nome do arquivo original
        
    Returns:
        Nome do arquivo sanitizado
    """
    # Remove caracteres inválidos no Windows
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Remove espaços múltiplos
    filename = re.sub(r'\s+', ' ', filename)
    
    # Limita o tamanho do nome
    max_length = 200
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:max_length - len(ext) - 1] + '.' + ext if ext else name[:max_length]
    
    return filename.strip()


def format_size(bytes_size: int) -> str:
    """
    Formata tamanho em bytes para formato legível
    
    Args:
        bytes_size: Tamanho em bytes
        
    Returns:
        String formatada (ex: "15.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"
