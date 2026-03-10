"""
Módulo de download de Reels do Instagram
"""

import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
from .logger import logger
from .utils import sanitize_filename, VideoPath


class InstagramDownloader:
    """Downloader especializado para Reels do Instagram"""
    
    def __init__(self):
        self.output_path = VideoPath.INSTAGRAM_PATH
    
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
    
    def download(self, url: str, custom_filename: Optional[str] = None, browser: Optional[str] = None) -> bool:
        """
        Baixa um Reel do Instagram
        
        Args:
            url: URL do Reel
            custom_filename: Nome customizado para o arquivo (opcional)
            browser: Nome do browser para extrair cookies (opcional)
            
        Returns:
            True se o download foi bem-sucedido, False caso contrário
        """
        try:
            logger.info(f"Analisando Reel do Instagram: {url}")
            
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
                    logger.error("Não foi possível obter informações do Reel")
                    return False
                
                title = info.get('title', 'instagram_reel')
                uploader = info.get('uploader', 'unknown')
                
                logger.info(f"De: @{uploader}")
                if title:
                    logger.info(f"Descrição: {title[:50]}...")
                
                # Preparar nome do arquivo
                if custom_filename:
                    filename = sanitize_filename(custom_filename)
                    if not filename.endswith('.mp4'):
                        filename += '.mp4'
                else:
                    # Usar ID do post ou timestamp para nome único
                    post_id = info.get('id', 'reel')
                    filename = sanitize_filename(f"{uploader}_{post_id}.mp4")
                
                output_template = str(self.output_path / filename)
                
                # Verificar se já existe
                if Path(output_template).exists():
                    logger.warning(f"Arquivo já existe: {filename}")
                    logger.info("Download ignorado para evitar duplicação")
                    return True
                
                # Configuração de download - melhor qualidade disponível
                ydl_opts = {
                    'format': 'best',  # Melhor qualidade disponível
                    'outtmpl': output_template,
                    'progress_hooks': [self._progress_hook],
                    'quiet': False,
                    'no_warnings': False,
                    # Opções adicionais para Instagram
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    },
                }
                
                if browser:
                    ydl_opts['cookiesfrombrowser'] = (browser,)
                    logger.info(f"Usando cookies do {browser}...")
                
                logger.info("Iniciando download...")
                
                # Download do vídeo
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                logger.success(f"✓ Reel salvo em: {output_template}")
                return True
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Erro ao baixar Reel: {str(e)}")
            if "Private" in str(e) or "login" in str(e).lower():
                logger.error("O Reel é privado ou requer login")
                if not browser:
                    logger.info("Dica: use --browser chrome (ou firefox, edge) para usar cookies do seu browser")
                else:
                    logger.info("Certifique-se de estar logado no Instagram no browser informado")
            elif "not available" in str(e).lower():
                logger.error("Reel indisponível ou removido")
            return False
            
        except yt_dlp.utils.ExtractorError as e:
            logger.error(f"Erro ao extrair informações: {str(e)}")
            logger.error("Verifique se a URL está correta")
            return False
            
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            logger.debug(f"Detalhes técnicos: {type(e).__name__}")
            return False
    
    def get_reel_info(self, url: str, browser: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtém informações sobre um Reel sem baixá-lo
        
        Args:
            url: URL do Reel
            browser: Nome do browser para extrair cookies (opcional)
            
        Returns:
            Dicionário com informações do Reel ou None se houver erro
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
                        'uploader': info.get('uploader'),
                        'duration': info.get('duration'),
                        'view_count': info.get('view_count'),
                        'like_count': info.get('like_count'),
                        'width': info.get('width'),
                        'height': info.get('height'),
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter informações: {str(e)}")
            return None
