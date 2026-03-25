"""
Interface CLI para Clipr - Download de vídeos do YouTube e Instagram
"""

import sys
import click
from pathlib import Path
from .downloader import VideoDownloader
from .logger import logger
from .utils import VideoPath
from . import __version__


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__, prog_name="Clipr")
def cli(ctx):
    """
    🎬 Clipr - Download inteligente de vídeos do YouTube e Instagram
    
    Baixa vídeos com qualidade máxima e organização automática.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('url', required=True)
@click.option('--name', '-n', help='Nome customizado para o arquivo (opcional)')
@click.option('--info', '-i', is_flag=True, help='Apenas exibir informações sem baixar')
@click.option('--browser', '-b', default=None,
              help='Usar cookies do browser para vídeos com restrição de idade (ex: chrome, firefox, edge, brave)')
@click.option('--transcribe', '-t', is_flag=True, help='Gerar transcrição após o download')
@click.option('--model', '-m', default='base', 
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Modelo Whisper a usar (padrão: base)')
def download(url: str, name: str, info: bool, browser: str, transcribe: bool, model: str):
    """
    Baixa um vídeo do YouTube ou Instagram Reel
    
    URL: Link do vídeo (YouTube ou Instagram Reel)
    
    Exemplos:
    
      clipr download https://www.youtube.com/watch?v=VIDEO_ID
      
      clipr download https://youtube.com/shorts/SHORT_ID
      
      clipr download https://www.instagram.com/reel/REEL_ID
      
      clipr download URL --name "meu_video"
      
      clipr download URL --info  (apenas visualizar informações)
      
      clipr download URL --browser chrome  (vídeos com restrição de idade)
      clipr download URL --transcribe  (gerar transcrição após download)
      
      clipr download URL --transcribe --model small  (transcrever com modelo pequeno)

      clipr download URL --transcribe  (gerar transcrição após download)
      
      clipr download URL --transcribe --model small  (transcrever com modelo pequeno)
    """
    
    logger.header(f"Clipr v{__version__} - Video Downloader")
    
    downloader = VideoDownloader()
    
    if browser:
        logger.info(f"Usando cookies do browser: {browser}")

    # Modo informação
    if info:
        logger.info("Obtendo informações do vídeo...")
        video_info = downloader.get_info(url, browser=browser)
        
        if video_info:
            logger.separator()
            logger.success("Informações do vídeo:")
            for key, value in video_info.items():
                if value is not None:
                    logger.info(f"  {key}: {value}")
            logger.separator()
        else:
            logger.error("Não foi possível obter informações do vídeo")
        
        return
    
    # Modo download
    logger.info("Iniciando processo de download...")
    logger.info(f"📂 Vídeos serão salvos em:")
    logger.info(f"   YouTube: {VideoPath.YOUTUBE_PATH}")
    logger.info(f"   Instagram: {VideoPath.INSTAGRAM_PATH}")
    logger.separator()
    
    success = downloader.download(url, name, browser=browser, transcribe=transcribe, transcribe_model=model)
    
    logger.separator()
    if success:
        logger.success("✅ Download concluído com sucesso!")
    else:
        logger.error("❌ Falha no download")
        sys.exit(1)


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--continue-on-error', '-c', is_flag=True, 
              help='Continuar mesmo se algum download falhar')
@click.option('--browser', '-b', default=None,
              help='Usar cookies do browser para vídeos com restrição de idade (ex: chrome, firefox, edge, brave)')
def batch(urls: tuple, continue_on_error: bool, browser: str):
    """
    Baixa múltiplos vídeos em lote
    
    URLS: Lista de URLs separadas por espaço
    
    Exemplo:
    
      clipr batch URL1 URL2 URL3
      
      clipr batch URL1 URL2 --continue-on-error
      
      clipr batch URL1 URL2 --browser chrome
    """
    logger.header(f"Clipr v{__version__} - Download em Lote")
    
    total = len(urls)
    logger.info(f"Total de {total} vídeos para baixar")
    logger.separator()
    
    downloader = VideoDownloader()
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls, 1):
        logger.info(f"\n[{i}/{total}] Processando: {url}")
        logger.separator()
        
        success = downloader.download(url, browser=browser)
        
        if success:
            successful += 1
            logger.success(f"✓ Vídeo {i}/{total} concluído")
        else:
            failed += 1
            logger.error(f"✗ Vídeo {i}/{total} falhou")
            
            if not continue_on_error:
                logger.error("Abortando lote devido a erro")
                break
        
        logger.separator()
    
    # Resumo final
    logger.header("Resumo do Download em Lote")
    logger.success(f"✓ Sucessos: {successful}")
    if failed > 0:
        logger.error(f"✗ Falhas: {failed}")
    logger.info(f"📊 Total: {successful + failed}/{total}")
    
    if failed > 0 and not continue_on_error:
        sys.exit(1)


@cli.command()
def paths():
    """
    Exibe os caminhos de saída configurados
    """
    logger.header("Caminhos de Saída")
    logger.info(f"YouTube: {VideoPath.YOUTUBE_PATH}")
    logger.info(f"Instagram: {VideoPath.INSTAGRAM_PATH}")
    
    # Verificar se os diretórios existem
    yt_exists = VideoPath.YOUTUBE_PATH.exists()
    ig_exists = VideoPath.INSTAGRAM_PATH.exists()
    
    logger.separator()
    logger.info(f"YouTube {'✓ existe' if yt_exists else '✗ não existe (será criado no primeiro download)'}")
    logger.info(f"Instagram {'✓ existe' if ig_exists else '✗ não existe (será criado no primeiro download)'}")


@cli.command()
def test():
    """
    Testa a instalação e configuração
    """
    logger.header("Teste de Instalação")
    
    # Verificar dependências
    try:
        import yt_dlp
        logger.success("✓ yt-dlp instalado")
    except ImportError:
        logger.error("✗ yt-dlp não encontrado")
        logger.info("  Instale com: pip install yt-dlp")
    
    try:
        import rich
        logger.success("✓ rich instalado")
    except ImportError:
        logger.error("✗ rich não encontrado")
        logger.info("  Instale com: pip install rich")
    
    try:
        import click
        logger.success("✓ click instalado")
    except ImportError:
        logger.error("✗ click não encontrado")
        logger.info("  Instale com: pip install click")
    
    # Verificar diretórios
    logger.separator()
    logger.info("Verificando diretórios...")
    
    try:
        VideoPath.ensure_directories()
        logger.success(f"✓ Diretórios criados/verificados")
        logger.info(f"  YouTube: {VideoPath.YOUTUBE_PATH}")
        logger.info(f"  Instagram: {VideoPath.INSTAGRAM_PATH}")
    except Exception as e:
        logger.error(f"✗ Erro ao criar diretórios: {e}")
    
    logger.separator()
    logger.success("Clipr está pronto para uso! 🎉")


@cli.command()
@click.argument('video_path', type=click.Path(exists=True), required=True)
@click.option('--platform', '-p', type=click.Choice(['youtube', 'instagram']),
              help='Plataforma (opcional, usa padrão baseado no diretório)')
@click.option('--model', '-m', default='base',
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Modelo Whisper a usar (padrão: base)')
@click.option('--language', '-l', 
              help='Código de idioma (ex: pt, en, es). Deixe vazio para auto-detect')
def transcribe(video_path: str, platform: str, model: str, language: str):
    """
    Transcreve um vídeo já baixado
    
    VIDEO_PATH: Caminho para o arquivo de vídeo (ou diretório com vídeos)
    
    Exemplos:
    
      clipr transcribe /caminho/para/video.mp4
      
      clipr transcribe /caminho/para/video.mp4 --model small
      
      clipr transcribe /caminho/para/video.mp4 --language pt
      
      clipr transcribe ~/Movies/Videos\\ baixados/Youtube/ (transcrever todos os vídeos)
    """
    from .transcriber import VideoTranscriber
    
    logger.header(f"Clipr v{__version__} - Video Transcriber")
    
    video_path_obj = Path(video_path)
    
    if not video_path_obj.exists():
        logger.error(f"Arquivo ou diretório não encontrado: {video_path}")
        sys.exit(1)
    
    transcriber = VideoTranscriber(model=model)
    
    # Se for diretório, transcrever todos os vídeos
    if video_path_obj.is_dir():
        logger.info(f"Processando diretório: {video_path}")
        logger.separator()
        
        # Encontrar vídeos no diretório
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm'}
        video_files = [
            f for f in video_path_obj.rglob('*')
            if f.is_file() and f.suffix.lower() in video_extensions and 'transcript' not in f.name
        ]
        
        if not video_files:
            logger.warning("Nenhum arquivo de vídeo encontrado no diretório")
            sys.exit(1)
        
        logger.info(f"Encontrados {len(video_files)} vídeo(s)")
        logger.separator()
        
        results = transcriber.transcribe_batch(
            video_files,
            output_dir=video_path_obj if not platform else None,
            language=language if language else None
        )
        
        logger.header("Resumo da Transcrição em Lote")
        successful = sum(1 for v in results.values() if v)
        failed = len(results) - successful
        
        logger.success(f"✓ Transcritos concluídos: {successful}")
        if failed > 0:
            logger.error(f"✗ Falhas: {failed}")
        
        if failed > 0:
            sys.exit(1)
    
    # Se for arquivo, transcrever apenas ele
    elif video_path_obj.is_file():
        logger.info(f"Transcrevendo arquivo: {video_path_obj.name}")
        logger.separator()
        
        # Determinar diretório de saída
        if platform:
            output_dir = VideoPath.get_transcript_path(platform)
        else:
            output_dir = video_path_obj.parent
        
        result = transcriber.transcribe_video(
            video_path_obj,
            output_dir=output_dir,
            language=language if language else None
        )
        
        if not result:
            logger.error("Falha ao transcrever vídeo")
            sys.exit(1)
    
    else:
        logger.error("Path inválido")
        sys.exit(1)


def main():
    """Ponto de entrada principal"""
    try:
        cli()
    except KeyboardInterrupt:
        logger.warning("\n\nDownload cancelado pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
