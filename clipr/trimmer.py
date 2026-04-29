"""
Módulo de corte interativo de vídeos via terminal
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from .logger import logger

console = Console()


def check_ffmpeg() -> bool:
    """Verifica se ffmpeg e ffprobe estão disponíveis no PATH."""
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([tool, "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    return True


def get_video_info(file_path: Path) -> Optional[dict]:
    """
    Obtém duração e resolução do vídeo via ffprobe.

    Returns:
        dict com 'duration' (float, segundos), 'width' (int|None), 'height' (int|None),
        ou None se ffprobe falhar.
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
        data = json.loads(result.stdout)  # json.loads aceita bytes (UTF-8)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return None

    duration = float(data.get("format", {}).get("duration", 0) or 0)
    width: Optional[int] = None
    height: Optional[int] = None

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            width = stream.get("width")
            height = stream.get("height")
            if not duration:
                duration = float(stream.get("duration", 0) or 0)
            break

    return {"duration": duration, "width": width, "height": height}


def fmt_seconds(total: float) -> str:
    """Formata segundos como HH:MM:SS (omite horas se zero)."""
    secs = int(total)
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def parse_timestamp(value: str, max_seconds: float) -> Optional[float]:
    """
    Converte string de timestamp em segundos.

    Formatos aceitos: HH:MM:SS, MM:SS ou número inteiro/decimal.

    Returns:
        Segundos como float dentro de [0, max_seconds], ou None se inválido.
    """
    value = value.strip()

    match = re.fullmatch(r"(\d+):(\d{2}):(\d{2})", value)
    if match:
        h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
        total = h * 3600 + m * 60 + s
        return float(total) if 0 <= total <= max_seconds else None

    match = re.fullmatch(r"(\d+):(\d{2})", value)
    if match:
        m, s = int(match.group(1)), int(match.group(2))
        total = m * 60 + s
        return float(total) if 0 <= total <= max_seconds else None

    try:
        total = float(value)
        return total if 0 <= total <= max_seconds else None
    except ValueError:
        return None


def _prompt_timestamp(label: str, max_seconds: float) -> float:
    """Faz prompt repetido até receber um timestamp válido."""
    hint = f"HH:MM:SS, MM:SS ou segundos (máx: {fmt_seconds(max_seconds)})"
    while True:
        raw = click.prompt(f"  {label} ({hint})", default="", show_default=False).strip()
        value = parse_timestamp(raw, max_seconds)
        if value is not None:
            return value
        logger.error(f"Timestamp inválido '{raw}'. Exemplos válidos: 01:30, 0:01:30, 90")


def _show_cuts_table(cuts: list[tuple[float, float]]) -> None:
    """Exibe tabela resumida dos cortes adicionados."""
    if not cuts:
        return
    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("#", style="dim", width=4)
    table.add_column("Início", justify="right")
    table.add_column("Fim", justify="right")
    table.add_column("Duração", justify="right", style="bold green")
    total_dur = 0.0
    for i, (s, e) in enumerate(cuts, 1):
        dur = e - s
        total_dur += dur
        table.add_row(str(i), fmt_seconds(s), fmt_seconds(e), fmt_seconds(dur))
    console.print(table)
    console.print(
        f"  [dim]Total de {len(cuts)} corte(s) · duração total: "
        f"[bold]{fmt_seconds(total_dur)}[/bold][/dim]"
    )


def interactive_cut_loop(duration: float) -> list[tuple[float, float]]:
    """
    Loop interativo que coleta os cortes desejados pelo usuário.

    Returns:
        Lista de tuplas (start, end) em segundos, na ordem definida pelo usuário.
    """
    cuts: list[tuple[float, float]] = []

    console.print()
    console.print(
        Panel(
            f"[bold]Duração total:[/bold] [cyan]{fmt_seconds(duration)}[/cyan]  "
            f"[dim]({duration:.1f}s)[/dim]\n\n"
            "[dim]Informe os pontos de início e fim de cada corte.\n"
            "Pressione Ctrl+C a qualquer momento para cancelar.[/dim]",
            title="[bold cyan]✂  Seleção de Cortes[/bold cyan]",
            border_style="cyan",
        )
    )

    while True:
        cut_num = len(cuts) + 1
        console.print(
            f"\n[bold cyan]─── Corte #{cut_num} "
            + "─" * max(0, 44 - len(str(cut_num)))
            + "[/bold cyan]"
        )

        start = _prompt_timestamp(f"Início do corte #{cut_num}", duration)

        while True:
            end = _prompt_timestamp(f"Fim do corte #{cut_num}", duration)
            if end > start:
                break
            logger.error(
                f"O fim ({fmt_seconds(end)}) deve ser maior que o início ({fmt_seconds(start)})"
            )

        cuts.append((start, end))
        console.print(
            f"  [green]✓[/green] Corte #{cut_num}: "
            f"[cyan]{fmt_seconds(start)}[/cyan] → [cyan]{fmt_seconds(end)}[/cyan]  "
            f"[bold green]({fmt_seconds(end - start)})[/bold green]"
        )

        console.print()
        _show_cuts_table(cuts)

        console.print()
        console.print("[bold]O que deseja fazer?[/bold]")
        console.print("  [1] Adicionar outro corte")
        console.print("  [2] Desfazer último corte")
        console.print("  [3] Finalizar e processar")
        console.print("  [0] Cancelar")

        while True:
            choice = click.prompt("  Escolha", default="", show_default=False).strip()
            if choice in ("0", "1", "2", "3"):
                break
            logger.error("Opção inválida. Digite 0, 1, 2 ou 3.")

        if choice == "0":
            logger.warning("Operação cancelada pelo usuário.")
            sys.exit(0)
        elif choice == "1":
            continue
        elif choice == "2":
            if cuts:
                removed = cuts.pop()
                logger.info(
                    f"Corte #{cut_num} removido: "
                    f"{fmt_seconds(removed[0])} → {fmt_seconds(removed[1])}"
                )
                if not cuts:
                    logger.info("Nenhum corte restante. Adicione pelo menos um corte.")
            else:
                logger.warning("Nenhum corte para desfazer.")
        elif choice == "3":
            if not cuts:
                logger.error("Adicione pelo menos um corte antes de finalizar.")
            else:
                break

    return cuts


def _ffmpeg_cut(
    input_path: Path,
    start: float,
    end: float,
    output_path: Path,
) -> bool:
    """Executa um único corte com FFmpeg usando -c copy."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", str(input_path),
        "-c", "copy",
        str(output_path),
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as exc:
        logger.error(f"FFmpeg falhou: {exc.stderr.decode(errors='replace').strip()}")
        return False


def process_cuts(
    input_path: Path,
    cuts: list[tuple[float, float]],
    output_path: Path,
    video_format: str = "mp4",
) -> bool:
    """
    Processa os cortes com FFmpeg e salva em output_path.

    Para um corte único faz o corte direto.
    Para múltiplos cortes gera segmentos temporários e os concatena via concat demuxer.

    Returns:
        True se bem-sucedido, False caso contrário.
    """
    if not cuts:
        logger.error("Nenhum corte para processar.")
        return False

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
        console=console,
    )

    with progress:
        # --- Corte único ---
        if len(cuts) == 1:
            start, end = cuts[0]
            task = progress.add_task("✂  Processando corte...", total=None)
            ok = _ffmpeg_cut(input_path, start, end, output_path)
            if ok:
                progress.update(task, description="✅ Corte concluído")
            return ok

        # --- Múltiplos cortes: segmentos temporários + concat ---
        tmp_dir = Path(tempfile.mkdtemp(prefix="clipr_trim_"))
        segment_paths: list[Path] = []

        try:
            for i, (start, end) in enumerate(cuts):
                seg = tmp_dir / f"seg_{i:03d}.{video_format}"
                task = progress.add_task(
                    f"✂  Cortando segmento {i + 1}/{len(cuts)}...", total=None
                )
                if not _ffmpeg_cut(input_path, start, end, seg):
                    return False
                segment_paths.append(seg)
                progress.update(task, description=f"✅ Segmento {i + 1}/{len(cuts)} pronto")

            # Gera lista para concat demuxer
            concat_list = tmp_dir / "concat.txt"
            concat_list.write_text(
                "\n".join(f"file '{p}'" for p in segment_paths),
                encoding="utf-8",
            )

            concat_task = progress.add_task("🔗 Concatenando segmentos...", total=None)
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list),
                "-c", "copy",
                str(output_path),
            ]
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                progress.update(concat_task, description="✅ Concatenação concluída")
                return True
            except subprocess.CalledProcessError as exc:
                progress.stop()
                logger.error(
                    f"Erro ao concatenar: {exc.stderr.decode(errors='replace').strip()}"
                )
                return False

        finally:
            for seg in segment_paths:
                try:
                    seg.unlink(missing_ok=True)
                except Exception:
                    pass
            try:
                (tmp_dir / "concat.txt").unlink(missing_ok=True)
                tmp_dir.rmdir()
            except Exception:
                pass
