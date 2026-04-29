"""
Módulo de extração de áudio de vídeos via terminal
"""

import json
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from .logger import logger

console = Console()

_AUDIO_CODECS = {
    "mp3":  ("libmp3lame", ["-q:a", "2"]),
    "m4a":  ("aac",        ["-b:a", "192k"]),
    "wav":  ("pcm_s16le",  []),
    "ogg":  ("libvorbis",  ["-q:a", "6"]),
    "flac": ("flac",       []),
}


def check_ffmpeg() -> bool:
    """Verifica se ffmpeg e ffprobe estão disponíveis no PATH."""
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([tool, "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    return True


def get_audio_info(file_path: Path) -> Optional[dict]:
    """
    Obtém informações do stream de áudio via ffprobe.

    Returns:
        dict com 'duration' (float, segundos), 'codec' (str|None), 'bitrate' (int|None),
        ou None se ffprobe falhar ou não houver stream de áudio.
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        str(file_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        data = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None

    duration = float(data.get("format", {}).get("duration", 0) or 0)
    bitrate_raw = data.get("format", {}).get("bit_rate")
    bitrate = int(bitrate_raw) // 1000 if bitrate_raw else None

    codec: Optional[str] = None
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "audio":
            codec = stream.get("codec_name")
            if not duration:
                duration = float(stream.get("duration", 0) or 0)
            if not bitrate and stream.get("bit_rate"):
                bitrate = int(stream["bit_rate"]) // 1000
            break

    if codec is None:
        return None

    return {"duration": duration, "codec": codec, "bitrate": bitrate}


def extract_audio(
    input_path: Path,
    output_path: Path,
    fmt: str = "mp3",
) -> bool:
    """
    Extrai o áudio de input_path e salva em output_path com o formato indicado.

    Returns:
        True se bem-sucedido, False caso contrário.
    """
    codec, extra_args = _AUDIO_CODECS.get(fmt, _AUDIO_CODECS["mp3"])

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", codec,
        *extra_args,
        str(output_path),
    ]

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
        console=console,
    )

    with progress:
        task = progress.add_task("🎵 Extraindo áudio...", total=None)
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            progress.update(task, description="✅ Extração concluída")
            return True
        except subprocess.CalledProcessError as exc:
            progress.stop()
            logger.error(f"FFmpeg falhou: {exc.stderr.decode(errors='replace').strip()}")
            return False


def show_audio_info_table(file_path: Path, info: dict) -> None:
    """Exibe tabela com informações do áudio do arquivo."""
    table = Table(show_header=False, border_style="cyan", box=None, padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column()

    from .trimmer import fmt_seconds

    table.add_row("Arquivo", file_path.name)
    table.add_row("Duração", f"{fmt_seconds(info['duration'])}  ({info['duration']:.1f}s)")
    if info.get("codec"):
        table.add_row("Codec de áudio", info["codec"])
    if info.get("bitrate"):
        table.add_row("Bitrate", f"{info['bitrate']} kbps")

    console.print(table)
