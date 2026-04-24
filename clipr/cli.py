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


# ---------------------------------------------------------------------------
# Seleção interativa de modelo Whisper
# ---------------------------------------------------------------------------

_MODEL_INFO = {
    "tiny":   {"size": "~39 MB",   "ram": "~1 GB",   "desc": "Rápido, menor precisão"},
    "base":   {"size": "~74 MB",   "ram": "~1 GB",   "desc": "Bom balanço (padrão)"},
    "small":  {"size": "~244 MB",  "ram": "~2 GB",   "desc": "Boa precisão"},
    "medium": {"size": "~769 MB",  "ram": "~5 GB",   "desc": "Alta precisão"},
    "large":  {"size": "~1,5 GB",  "ram": "~10 GB",  "desc": "Melhor precisão"},
}


def _pick_model_interactively() -> str | None:
    """Exibe menu de seleção de modelo. Retorna o nome escolhido ou None se desistir."""
    models = list(_MODEL_INFO.keys())

    click.echo("\n┌─ Escolha um modelo de transcrição Whisper ──────────────────────────┐")
    for i, name in enumerate(models, 1):
        info = _MODEL_INFO[name]
        click.echo(
            f"│  [{i}] {name:<8}  Download: {info['size']:<10}"
            f"  RAM: {info['ram']:<8}  {info['desc']:<28}│"
        )
    click.echo("│  [0] Cancelar                                                        │")
    click.echo("└──────────────────────────────────────────────────────────────────────┘\n")

    while True:
        raw = click.prompt("Escolha", default="", show_default=False).strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(models):
            return models[int(raw) - 1]
        click.echo(f"  Opção inválida. Digite um número de 0 a {len(models)}.")


def _whisper_cache_dir() -> Path:
    import os
    base = os.getenv("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "whisper"


def _whisper_model_path(model_name: str) -> Path:
    return _whisper_cache_dir() / f"{model_name}.pt"


def _delete_old_model(model_name: str) -> None:
    path = _whisper_model_path(model_name)
    if path.exists():
        path.unlink()
        logger.warning(f"Modelo {model_name} excluído de {path}")
    else:
        logger.info(f"Modelo {model_name} não estava baixado localmente")


def _resolve_model(explicit_model: str | None) -> str | None:
    """
    Retorna o modelo a usar para transcrição.

    - Se `explicit_model` foi passado explicitamente → usa e salva como preferência.
    - Se não → verifica preferência salva; na ausência dela, exibe o picker.
    - Retorna None se o usuário cancelar.
    """
    from . import config as cfg

    if explicit_model is not None:
        cfg.set("preferred_transcription_model", explicit_model)
        return explicit_model

    saved = cfg.get("preferred_transcription_model")
    if saved:
        logger.info(f"Usando modelo de transcrição salvo: {saved}")
        return saved

    # Primeira vez: mostra o picker
    chosen = _pick_model_interactively()
    if chosen:
        cfg.set("preferred_transcription_model", chosen)
    return chosen


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
@click.version_option(version=__version__, prog_name="Clipr")
def cli(ctx):
    """
    🎬 Clipr - Download inteligente de vídeos do YouTube e Instagram

    Baixa vídeos com qualidade máxima e organização automática.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('url', required=True)
@click.option('--name', '-n', help='Nome customizado para o arquivo (opcional)')
@click.option('--info', '-i', is_flag=True, help='Apenas exibir informações sem baixar')
@click.option('--browser', '-b', default=None,
              help='Usar cookies do browser para vídeos com restrição de idade (ex: chrome, firefox, edge, brave)')
@click.option('--audio-only', '-x', is_flag=True, help='Baixar somente o áudio em .mp3')
@click.option('--transcribe', '-t', is_flag=True, help='Gerar transcrição após o download')
@click.option('--model', '-m', default=None,
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Modelo Whisper a usar (omita para usar preferência salva ou escolher interativamente)')
def download(url: str, name: str, info: bool, browser: str, audio_only: bool, transcribe: bool, model: str):
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

      clipr download --audio-only URL  (baixar somente o áudio em mp3)

      clipr download -x URL  (alias curto para --audio-only)

      clipr download https://www.tiktok.com/@usuario/video/ID  (TikTok)

      clipr download https://vm.tiktok.com/SHORTCODE  (TikTok link curto)

      clipr download URL --transcribe  (gerar transcrição após download)

      clipr download URL --transcribe --model small  (transcrever com modelo específico)
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

    # Resolver modelo antes de iniciar o download, para o usuário poder desistir
    resolved_model = None
    if transcribe:
        resolved_model = _resolve_model(model)
        if resolved_model is None:
            logger.warning("Transcrição cancelada. Abortando.")
            sys.exit(0)
        logger.info(f"Modelo de transcrição: {resolved_model}")

    # Modo download
    logger.info("Iniciando processo de download...")
    if audio_only:
        logger.info("Modo áudio apenas ativado: será gerado um arquivo .mp3")
    logger.info("📂 Arquivos serão salvos em:")
    logger.info(f"   YouTube: {VideoPath.YOUTUBE_PATH}")
    logger.info(f"   Instagram: {VideoPath.INSTAGRAM_PATH}")
    logger.info(f"   TikTok: {VideoPath.TIKTOK_PATH}")
    logger.separator()

    success = downloader.download(
        url,
        name,
        browser=browser,
        audio_only=audio_only,
        transcribe=transcribe,
        transcribe_model=resolved_model or "base",
    )

    logger.separator()
    if success:
        logger.success("✅ Download concluído com sucesso!")
    else:
        logger.error("❌ Falha no download")
        sys.exit(1)


@cli.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('urls', nargs=-1, required=True)
@click.option('--continue-on-error', '-c', is_flag=True,
              help='Continuar mesmo se algum download falhar')
@click.option('--browser', '-b', default=None,
              help='Usar cookies do browser para vídeos com restrição de idade (ex: chrome, firefox, edge, brave)')
@click.option('--audio-only', '-x', is_flag=True, help='Baixar somente o áudio em .mp3 para cada URL')
def batch(urls: tuple, continue_on_error: bool, browser: str, audio_only: bool):
    """
    Baixa múltiplos vídeos em lote

    URLS: Lista de URLs separadas por espaço

    Exemplo:

      clipr batch URL1 URL2 URL3

      clipr batch URL1 URL2 --continue-on-error

      clipr batch URL1 URL2 --browser chrome

      clipr batch --audio-only URL1 URL2

      clipr batch -x URL1 URL2  (alias curto para --audio-only)

      clipr batch https://vm.tiktok.com/AAA https://vm.tiktok.com/BBB  (TikTok em lote)
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

        success = downloader.download(url, browser=browser, audio_only=audio_only)

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
    logger.info(f"TikTok: {VideoPath.TIKTOK_PATH}")

    yt_exists = VideoPath.YOUTUBE_PATH.exists()
    ig_exists = VideoPath.INSTAGRAM_PATH.exists()
    tt_exists = VideoPath.TIKTOK_PATH.exists()

    logger.separator()
    logger.info(f"YouTube {'✓ existe' if yt_exists else '✗ não existe (será criado no primeiro download)'}")
    logger.info(f"Instagram {'✓ existe' if ig_exists else '✗ não existe (será criado no primeiro download)'}")
    logger.info(f"TikTok {'✓ existe' if tt_exists else '✗ não existe (será criado no primeiro download)'}")


@cli.command()
def test():
    """
    Testa a instalação e configuração
    """
    logger.header("Teste de Instalação")

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

    logger.separator()
    logger.info("Verificando diretórios...")

    try:
        VideoPath.ensure_directories()
        logger.success("✓ Diretórios criados/verificados")
        logger.info(f"  YouTube: {VideoPath.YOUTUBE_PATH}")
        logger.info(f"  Instagram: {VideoPath.INSTAGRAM_PATH}")
    except Exception as e:
        logger.error(f"✗ Erro ao criar diretórios: {e}")

    logger.separator()
    logger.success("Clipr está pronto para uso! 🎉")


_MEDIA_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.mp3', '.m4a', '.ogg', '.wav'}
_TRANSCRIPT_EXTENSIONS = {'.txt', '.srt', '.json', '.vtt'}


def _has_transcript(media_file: Path) -> bool:
    """Retorna True se já existe um arquivo de transcrição para o media_file."""
    for ext in _TRANSCRIPT_EXTENSIONS:
        if (media_file.parent / (media_file.stem + ext)).exists():
            return True
    transcripts_dir = media_file.parent / "Transcripts"
    if transcripts_dir.exists():
        for ext in _TRANSCRIPT_EXTENSIONS:
            if (transcripts_dir / (media_file.stem + ext)).exists():
                return True
    return False


def _collect_untranscribed() -> list[Path]:
    """Varre todas as pastas de download e retorna arquivos sem transcrição."""
    search_dirs = [
        VideoPath.YOUTUBE_PATH,
        VideoPath.INSTAGRAM_PATH,
        VideoPath.TIKTOK_PATH,
    ]
    result = []
    for base in search_dirs:
        if not base.exists():
            continue
        for f in sorted(base.rglob('*')):
            if (
                f.is_file()
                and f.suffix.lower() in _MEDIA_EXTENSIONS
                and 'transcript' not in f.name.lower()
                and not _has_transcript(f)
            ):
                result.append(f)
    return result


def _pick_untranscribed_interactively() -> Path | None:
    """
    Lista vídeos/áudios sem transcrição e deixa o usuário escolher um.
    Retorna o Path escolhido ou None se cancelar.
    """
    files = _collect_untranscribed()

    if not files:
        click.echo("\n  Nenhum arquivo sem transcrição encontrado nas pastas de download.")
        return None

    # Agrupa por pasta-pai para facilitar leitura
    click.echo(f"\n┌─ Arquivos sem transcrição ({len(files)} encontrado(s)) ──────────────────┐")
    for i, f in enumerate(files, 1):
        try:
            rel = f.relative_to(VideoPath.BASE_PATH)
        except ValueError:
            rel = f
        click.echo(f"│  [{i:>2}] {str(rel):<60}│")
    click.echo("│  [ 0] Cancelar" + " " * 55 + "│")
    click.echo("└──────────────────────────────────────────────────────────────────────┘\n")

    while True:
        raw = click.prompt("Escolha o arquivo", default="", show_default=False).strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(files):
            return files[int(raw) - 1]
        click.echo(f"  Opção inválida. Digite um número de 0 a {len(files)}.")


def _pick_file_with_explorer() -> Path | None:
    """Abre o explorador de arquivos via tkinter e retorna o arquivo selecionado."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        logger.error("tkinter não está disponível neste ambiente.")
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    extensions = " ".join(f"*{e}" for e in sorted(_MEDIA_EXTENSIONS))
    chosen = filedialog.askopenfilename(
        title="Selecione um vídeo ou áudio para transcrever",
        filetypes=[("Vídeos e áudios", extensions), ("Todos os arquivos", "*.*")],
        initialdir=str(VideoPath.BASE_PATH) if VideoPath.BASE_PATH.exists() else str(Path.home()),
    )
    root.destroy()

    if not chosen:
        return None
    return Path(chosen)


def _pick_transcribe_source() -> Path | None:
    """Menu principal de seleção de fonte para transcrição."""
    click.echo("\n┌─ Como deseja selecionar o arquivo? ──────────────────────────────────┐")
    click.echo("│  [1] Listar vídeos/áudios baixados sem transcrição                   │")
    click.echo("│  [2] Abrir explorador de arquivos                                    │")
    click.echo("│  [0] Cancelar                                                        │")
    click.echo("└──────────────────────────────────────────────────────────────────────┘\n")

    while True:
        raw = click.prompt("Escolha", default="", show_default=False).strip()
        if raw == "0":
            return None
        if raw == "1":
            return _pick_untranscribed_interactively()
        if raw == "2":
            return _pick_file_with_explorer()
        click.echo("  Opção inválida. Digite 0, 1 ou 2.")


@cli.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('video_path', type=click.Path(), required=False, default=None)
@click.option('--platform', '-p', type=click.Choice(['youtube', 'instagram']),
              help='Plataforma (opcional, usa padrão baseado no diretório)')
@click.option('--model', '-m', default=None,
              type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
              help='Modelo Whisper a usar (omita para usar preferência salva ou escolher interativamente)')
@click.option('--language', '-l',
              help='Código de idioma (ex: pt, en, es). Deixe vazio para auto-detect')
def transcribe(video_path: str, platform: str, model: str, language: str):
    """
    Transcreve um vídeo já baixado

    VIDEO_PATH: Caminho para o arquivo de vídeo (ou diretório com vídeos).
    Se omitido, exibe um menu para selecionar o arquivo interativamente.

    Exemplos:

      clipr transcribe /caminho/para/video.mp4

      clipr transcribe /caminho/para/video.mp4 --model small

      clipr transcribe /caminho/para/video.mp4 --language pt

      clipr transcribe  (selecionar arquivo interativamente)

      clipr transcribe ~/Movies/Videos\\ baixados/Youtube/ (transcrever todos os vídeos)

      clipr set-model  (trocar o modelo salvo e apagar o anterior)
    """
    from .transcriber import VideoTranscriber

    logger.header(f"Clipr v{__version__} - Video Transcriber")

    # Sem argumento: abre o seletor interativo
    if video_path is None:
        chosen = _pick_transcribe_source()
        if chosen is None:
            logger.warning("Transcrição cancelada.")
            sys.exit(0)
        video_path = str(chosen)

    video_path_obj = Path(video_path)

    if not video_path_obj.exists():
        logger.error(f"Arquivo ou diretório não encontrado: {video_path}")
        sys.exit(1)

    resolved_model = _resolve_model(model)
    if resolved_model is None:
        logger.warning("Transcrição cancelada.")
        sys.exit(0)

    logger.info(f"Modelo de transcrição: {resolved_model}")

    transcriber = VideoTranscriber(model=resolved_model)

    # Se for diretório, transcrever todos os vídeos
    if video_path_obj.is_dir():
        logger.info(f"Processando diretório: {video_path}")
        logger.separator()

        video_files = [
            f for f in video_path_obj.rglob('*')
            if f.is_file() and f.suffix.lower() in _MEDIA_EXTENSIONS and 'transcript' not in f.name.lower()
        ]

        if not video_files:
            logger.warning("Nenhum arquivo de mídia encontrado no diretório")
            sys.exit(1)

        logger.info(f"Encontrados {len(video_files)} arquivo(s)")
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


@cli.command(name="set-model")
def set_model():
    """
    Troca o modelo Whisper salvo para transcrições

    Exibe o seletor interativo, apaga o modelo anterior baixado e salva a nova preferência.
    """
    from . import config as cfg

    current = cfg.get("preferred_transcription_model")

    if current:
        logger.info(f"Modelo atual: {current}")
    else:
        logger.info("Nenhum modelo salvo ainda")

    logger.separator()
    chosen = _pick_model_interactively()

    if chosen is None:
        logger.warning("Operação cancelada. Nenhuma alteração feita.")
        sys.exit(0)

    if chosen == current:
        logger.info(f"Modelo '{chosen}' já é o modelo salvo. Nenhuma alteração feita.")
        return

    if current:
        _delete_old_model(current)

    cfg.set("preferred_transcription_model", chosen)
    logger.success(f"Modelo salvo: {chosen}")


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
