"""
Módulo de download de vídeos do TikTok
"""

import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
from .logger import logger
from .utils import sanitize_filename, VideoPath

BROWSER_FALLBACK_ORDER = ["chrome", "firefox", "edge", "brave", "zen", "safari"]

TIKTOK_HEADERS = {
    "Referer": "https://www.tiktok.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


class TikTokDownloader:
    """Downloader especializado para vídeos do TikTok"""

    def __init__(self):
        self.output_path = VideoPath.TIKTOK_PATH

    def _resolve_browser(self, browser: Optional[str]) -> Optional[str]:
        """
        Retorna o browser a usar para cookies.
        Se explícito, usa direto. Se None, tenta a ordem de fallback.
        Retorna None se nenhum browser estiver disponível.
        """
        if browser:
            return browser

        for candidate in BROWSER_FALLBACK_ORDER:
            try:
                opts = {"quiet": True, "no_warnings": True, "cookiesfrombrowser": (candidate,)}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.cookiejar  # acessa para forçar carga; falha se browser ausente
                return candidate
            except Exception:
                continue

        return None

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            speed = d.get("speed", 0)

            if total > 0:
                percent = (downloaded / total) * 100
                speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed else "N/A"
                logger.info(f"Baixando: {percent:.1f}% - Velocidade: {speed_str}")

        elif d["status"] == "finished":
            logger.success("Download concluído, processando...")

    def download(
        self,
        url: str,
        custom_filename: Optional[str] = None,
        browser: Optional[str] = None,
        audio_only: bool = False,
    ) -> Optional[Path]:
        """
        Baixa um vídeo do TikTok.

        Args:
            url: URL do vídeo
            custom_filename: Nome customizado para o arquivo (opcional)
            browser: Browser para extrair cookies; se None tenta chrome/firefox/safari
            audio_only: Se True, extrai apenas o áudio em mp3

        Returns:
            Path do arquivo se bem-sucedido, None caso contrário
        """
        try:
            resolved_browser = self._resolve_browser(browser)

            if not resolved_browser:
                logger.error("Nenhum browser com cookies do TikTok encontrado")
                logger.info(
                    "Abra o TikTok em um dos browsers abaixo e tente novamente:\n"
                    "  • Google Chrome\n"
                    "  • Mozilla Firefox\n"
                    "  • Microsoft Edge\n"
                    "  • Brave\n"
                    "  • Zen\n"
                    "  • Safari\n"
                    "Ou passe o browser explicitamente com: --browser chrome"
                )
                return None

            logger.info(f"Analisando vídeo do TikTok: {url}")
            logger.info(f"Usando cookies do browser: {resolved_browser}")

            ydl_opts_info = {
                "quiet": True,
                "no_warnings": True,
                "cookiesfrombrowser": (resolved_browser,),
                "http_headers": TIKTOK_HEADERS,
            }

            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    logger.error("Não foi possível obter informações do vídeo")
                    return None

                title = info.get("title", "tiktok_video")
                uploader = info.get("uploader") or info.get("creator") or "unknown"

                logger.info(f"De: @{uploader}")
                if title:
                    logger.info(f"Título: {title[:60]}")

                if custom_filename:
                    filename = sanitize_filename(custom_filename)
                else:
                    post_id = info.get("id", "video")
                    filename = sanitize_filename(f"{uploader}_{post_id}")

                extension = ".mp3" if audio_only else ".mp4"
                current_suffix = Path(filename).suffix.lower()
                known_extensions = {".mp3", ".mp4", ".m4a", ".webm", ".mov", ".avi", ".mkv"}
                if current_suffix in known_extensions:
                    filename = str(Path(filename).with_suffix(extension))
                elif not filename.endswith(extension):
                    filename += extension

                final_output_path = self.output_path / filename
                output_template = (
                    str(final_output_path.with_suffix(".%(ext)s")) if audio_only else str(final_output_path)
                )

                if final_output_path.exists():
                    logger.warning(f"Arquivo já existe: {filename}")
                    logger.info("Download ignorado para evitar duplicação")
                    return final_output_path

                if audio_only:
                    logger.info("Modo áudio apenas ativado: extraindo o melhor áudio disponível em mp3")
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": output_template,
                        "progress_hooks": [self._progress_hook],
                        "quiet": False,
                        "no_warnings": False,
                        "cookiesfrombrowser": (resolved_browser,),
                        "http_headers": TIKTOK_HEADERS,
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            }
                        ],
                    }
                else:
                    ydl_opts = {
                        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
                        "outtmpl": output_template,
                        "merge_output_format": "mp4",
                        "progress_hooks": [self._progress_hook],
                        "quiet": False,
                        "no_warnings": False,
                        "cookiesfrombrowser": (resolved_browser,),
                        "http_headers": TIKTOK_HEADERS,
                    }

                logger.info("Iniciando download...")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                saved_label = "Áudio" if audio_only else "Vídeo"
                logger.success(f"✓ {saved_label} salvo em: {final_output_path}")
                return final_output_path

        except yt_dlp.utils.DownloadError as e:
            err = str(e)
            logger.error(f"Erro ao baixar vídeo do TikTok: {err}")
            if "403" in err or "forbidden" in err.lower():
                logger.error("Acesso negado pelo TikTok (403 Forbidden)")
                logger.info(
                    "Certifique-se de estar logado no TikTok no browser informado e tente novamente"
                )
            elif "private" in err.lower() or "login" in err.lower():
                logger.error("O vídeo é privado ou requer login")
                logger.info("Faça login no TikTok no browser e tente novamente")
            elif "unavailable" in err.lower() or "removed" in err.lower():
                logger.error("Vídeo indisponível ou removido")
            return None

        except yt_dlp.utils.ExtractorError as e:
            logger.error(f"Erro ao extrair informações: {str(e)}")
            logger.error("Verifique se a URL está correta")
            return None

        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return None

    def get_video_info(self, url: str, browser: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Obtém informações sobre um vídeo sem baixá-lo"""
        try:
            resolved_browser = self._resolve_browser(browser)
            ydl_opts: Dict[str, Any] = {
                "quiet": True,
                "no_warnings": True,
                "http_headers": TIKTOK_HEADERS,
            }
            if resolved_browser:
                ydl_opts["cookiesfrombrowser"] = (resolved_browser,)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info:
                    return {
                        "title": info.get("title"),
                        "uploader": info.get("uploader") or info.get("creator"),
                        "duration": info.get("duration"),
                        "view_count": info.get("view_count"),
                        "like_count": info.get("like_count"),
                        "width": info.get("width"),
                        "height": info.get("height"),
                    }

            return None

        except Exception as e:
            logger.error(f"Erro ao obter informações: {str(e)}")
            return None
