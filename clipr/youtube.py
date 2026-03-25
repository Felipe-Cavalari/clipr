"""
Módulo de download de vídeos do YouTube
"""

import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
from .logger import logger
from .utils import sanitize_filename, VideoPath


class YouTubeDownloader:
    """Downloader especializado para vídeos do YouTube"""
    
    def __init__(self):
        self.output_path = VideoPath.YOUTUBE_PATH
    
    def _is_short_video(self, info_dict: Dict[str, Any]) -> bool:
        """
        Determina se o vídeo é um Short (vertical)
        
        Args:
            info_dict: Informações do vídeo retornadas pelo yt-dlp
            
        Returns:
            True se for Short (vertical), False caso contrário
        """
        # Verifica se é um Short pela URL
        if 'shorts' in info_dict.get('webpage_url', ''):
            return True
        
        # Verifica pela proporção do vídeo
        width = info_dict.get('width', 0)
        height = info_dict.get('height', 0)
        
        if width > 0 and height > 0:
            aspect_ratio = width / height
            # Considera Short se a proporção for próxima de vertical (9:16)
            return aspect_ratio < 0.7  # Aproximadamente 9:16 ou mais vertical
        
        return False
    
    def _get_format_selector(self, is_short: bool) -> str:
        """
        Retorna o seletor de formato baseado no tipo de vídeo
        
        Args:
            is_short: Se o vídeo é um Short
            
        Returns:
            String de seleção de formato para yt-dlp
        """
        if is_short:
            # Para Shorts (verticais): priorizar 1080x1920 ou melhor qualidade vertical
            return (
                "bestvideo[ext=mp4][height<=1920][width<=1080]+bestaudio[ext=m4a]/"
                "bestvideo[ext=mp4][height<=1920][width<=1080]+bestaudio[acodec^=mp4a]/"
                "best[ext=mp4][height<=1920]/best[ext=mp4]"
            )
        else:
            # Para vídeos horizontais: priorizar 1920x1080 (Full HD)
            return (
                "bestvideo[ext=mp4][height<=1080][width<=1920]+bestaudio[ext=m4a]/"
                "bestvideo[ext=mp4][height<=1080][width<=1920]+bestaudio[acodec^=mp4a]/"
                "best[ext=mp4][height<=1080]/best[ext=mp4]"
            )
    
    def _progress_hook(self, d: Dict[str, Any]) -> None:
        """
        Hook para exibir progresso do download
        
        Args:
            d: Dicionário com informações de progresso
        """
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            speed = d.get('speed', 0)
            
            if total > 0:
                percent = (downloaded / total) * 100
                speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "N/A"
                logger.info(f"Baixando: {percent:.1f}% - Velocidade: {speed_str}")
        
        elif d['status'] == 'finished':
            logger.success("Download concluído, processando...")
    
    def download(self, url: str, custom_filename: Optional[str] = None, browser: Optional[str] = None) -> Optional[Path]:

        """
        Baixa um vídeo do YouTube
        
        Args:
            url: URL do vídeo
            custom_filename: Nome customizado para o arquivo (opcional)
            browser: Nome do browser para extrair cookies, ex: chrome, firefox, edge (opcional)
            
        Returns:
            Path do arquivo se o download foi bem-sucedido, None caso contrário
        """
        try:
            logger.info(f"Analisando vídeo: {url}")
            
            # Primeiro, obter informações do vídeo
            ydl_opts_info = {
                'quiet': True,
                'no_warnings': True,
            }
            if browser:
                ydl_opts_info['cookiesfrombrowser'] = (browser,)
            
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logger.error("Não foi possível obter informações do vídeo")
                    return False
                
                # Determinar tipo de vídeo
                is_short = self._is_short_video(info)
                video_type = "Short (vertical)" if is_short else "Vídeo horizontal"
                title = info.get('title', 'video')
                
                logger.info(f"Tipo: {video_type}")
                logger.info(f"Título: {title}")
                
                # Preparar nome do arquivo
                if custom_filename:
                    filename = sanitize_filename(custom_filename)
                    # Garante extensão
                    if not filename.endswith('.mp4'):
                        filename += '.mp4'
                else:
                    filename = sanitize_filename(title) + '.mp4'
                
                output_template = str(self.output_path / filename)
                
                # Verificar se já existe
                if Path(output_template).exists():
                    logger.warning(f"Arquivo já existe: {filename}")
                    logger.info("Download ignorado para evitar duplicação")
                    return Path(output_template)
                
                # Configuração de download
                format_selector = self._get_format_selector(is_short)
                
                ydl_opts = {
                    'format': format_selector,
                    'outtmpl': output_template,
                    'merge_output_format': 'mp4',
                    'progress_hooks': [self._progress_hook],
                    'quiet': False,
                    'no_warnings': False,
                    # Opções para garantir melhor qualidade
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                }
                
                if browser:
                    ydl_opts['cookiesfrombrowser'] = (browser,)
                    logger.info(f"Usando cookies do {browser}...")
                
                logger.info("Iniciando download...")
                
                # Download do vídeo
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                logger.success(f"✓ Vídeo salvo em: {output_template}")
                return Path(output_template)
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Erro ao baixar vídeo: {str(e)}")
            if "DRM" in str(e) or "drm" in str(e).lower():
                logger.error("Este vídeo é protegido por DRM (Widevine/EME)")
                logger.info("Vídeos com DRM não podem ser baixados — a criptografia é aplicada pelo próprio conteúdo")
                logger.info("Isso afeta filmes, séries e conteúdos licenciados no YouTube")
            elif "Private video" in str(e) or "members-only" in str(e):
                logger.error("O vídeo é privado ou restrito")
            elif "Video unavailable" in str(e):
                logger.error("Vídeo indisponível ou removido")
            elif "age" in str(e).lower() or "confirm your age" in str(e).lower():
                logger.error("Vídeo restrito por idade")
                if not browser:
                    logger.info("Dica: use --browser chrome (ou firefox, edge) para usar cookies do seu browser")
            return None
            
        except yt_dlp.utils.ExtractorError as e:
            logger.error(f"Erro ao extrair informações: {str(e)}")
            logger.error("Verifique se a URL está correta")
            return None
            
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return None
    
    def get_video_info(self, url: str, browser: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtém informações sobre um vídeo sem baixá-lo
        
        Args:
            url: URL do vídeo
            browser: Nome do browser para extrair cookies (opcional)
            
        Returns:
            Dicionário com informações do vídeo ou None se houver erro
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            if browser:
                ydl_opts['cookiesfrombrowser'] = (browser,)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    return {
                        'title': info.get('title'),
                        'duration': info.get('duration'),
                        'uploader': info.get('uploader'),
                        'view_count': info.get('view_count'),
                        'width': info.get('width'),
                        'height': info.get('height'),
                        'is_short': self._is_short_video(info),
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter informações: {str(e)}")
            return None
