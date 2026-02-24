"""
Módulo de configuração de logging com Rich
"""

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.text import Text
from enum import Enum


class LogLevel(Enum):
    """Níveis de log"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class Logger:
    """Logger customizado com Rich para CLI"""
    
    def __init__(self):
        self.console = Console()
    
    def info(self, message: str) -> None:
        """Log de informação"""
        self.console.print(f"[blue]ℹ[/blue] {message}")
    
    def success(self, message: str) -> None:
        """Log de sucesso"""
        self.console.print(f"[green]✓[/green] {message}")
    
    def warning(self, message: str) -> None:
        """Log de aviso"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
    
    def error(self, message: str) -> None:
        """Log de erro"""
        self.console.print(f"[red]✗[/red] {message}")
    
    def debug(self, message: str) -> None:
        """Log de debug"""
        self.console.print(f"[dim]🔍 {message}[/dim]")
    
    def header(self, title: str) -> None:
        """Exibe um cabeçalho destacado"""
        text = Text(title, style="bold cyan")
        panel = Panel(text, border_style="cyan")
        self.console.print(panel)
    
    def separator(self) -> None:
        """Exibe um separador visual"""
        self.console.print("─" * 60, style="dim")
    
    def create_progress(self) -> Progress:
        """
        Cria uma barra de progresso para downloads
        
        Returns:
            Objeto Progress configurado
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        )


# Instância global do logger
logger = Logger()
