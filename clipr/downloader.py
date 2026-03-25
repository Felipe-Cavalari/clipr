"""
Módulo principal de download - Gerenciador unificado
"""

from typing import Optional
from pathlib import Path
from .youtube import YouTubeDownloader
from .instagram import InstagramDownloader
from .transcriber import VideoTranscriber
from .utils import URLValidator, VideoPath
from .logger import logger


class VideoDownloader:
    """
    Gerenciador unificado de downloads de vídeos
    Detecta automaticamente a plataforma e delega para o downloader apropriado
    """
    
    def __init__(self):
        """Inicializa os downloaders e garante que os diretórios existam"""
        VideoPath.ensure_directories()
        self.youtube = YouTubeDownloader()
        self.instagram = InstagramDownloader()
        self.transcriber = VideoTranscriber()
    
    def download(self, url: str, custom_filename: Optional[str] = None, browser: Optional[str] = None, transcribe: bool = False, transcribe_model: str = "base") -> bool:

        """
        Baixa um vídeo detectando automaticamente a plataforma
        
        Args:
            url: URL do vídeo (YouTube ou Instagram)
            custom_filename: Nome customizado para o arquivo (opcional)
            browser: Nome do browser para extrair cookies (ex: chrome, firefox, edge)
            transcribe: Se True, gera transcrição após o download
            transcribe_model: Modelo Whisper a usar (tiny, base, small, medium, large)
            
        Returns:
            True se o download foi bem-sucedido, False caso contrário
        """
        # Validar e identificar plataforma
        is_valid, platform = URLValidator.validate_and_identify(url)
        
        if not is_valid:
            logger.error("URL inválida ou não suportada")
            logger.info("Plataformas suportadas: YouTube (vídeos e Shorts), Instagram (Reels)")
            return False
        
        logger.info(f"Plataforma detectada: {platform.upper()}")
        logger.separator()
        
        # Delegar para o downloader apropriado
        try:
            video_path = None
            
            if platform == "youtube":
                video_path = self.youtube.download(url, custom_filename, browser=browser)
            elif platform == "instagram":
                video_path = self.instagram.download(url, custom_filename, browser=browser)
            else:
                logger.error(f"Plataforma não suportada: {platform}")
                return False
            
            # Se download foi bem-sucedido e transcrição foi solicitada
            if video_path and transcribe:
                logger.separator()
                logger.info("Iniciando transcrição do vídeo...")
                logger.separator()
                
                output_dir = VideoPath.get_transcript_path(platform)
                result = self.transcriber.transcribe_video(
                    video_path,
                    output_dir=output_dir,
                    language=None  # Auto-detect
                )
                
                if result:
                    logger.success("Transcrição concluída com sucesso!")
                else:
                    logger.warning("Falha na transcrição, mas o vídeo foi baixado")
            
            return True
                
        except Exception as e:
            logger.error(f"Erro crítico durante o download: {str(e)}")
            return False
    
    def get_info(self, url: str, browser: Optional[str] = None) -> Optional[dict]:
        """
        Obtém informações sobre um vídeo sem baixá-lo
        
        Args:
            url: URL do vídeo
            browser: Nome do browser para extrair cookies (opcional)
            
        Returns:
            Dicionário com informações ou None se houver erro
        """
        is_valid, platform = URLValidator.validate_and_identify(url)
        
        if not is_valid:
            logger.error("URL inválida")
            return None
        
        try:
            if platform == "youtube":
                return self.youtube.get_video_info(url, browser=browser)
            elif platform == "instagram":
                return self.instagram.get_reel_info(url, browser=browser)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter informações: {str(e)}")
            return None
