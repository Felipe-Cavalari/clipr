"""
Módulo de transcrição de vídeos usando OpenAI Whisper
"""

import whisper
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import timedelta
from .logger import logger
from .utils import sanitize_filename, VideoPath


class VideoTranscriber:
    """Classe responsável por transcrever vídeos usando Whisper"""

    # Modelos disponíveis do Whisper
    # tiny: ~39M, base: ~74M, small: ~244M, medium: ~769M, large: ~1550M
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]
    DEFAULT_MODEL = "base"

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Inicializa o transcritor

        Args:
            model: Modelo do Whisper a usar (tiny, base, small, medium, large)
                   Padrão: base (bom balanço entre velocidade e qualidade)
        """
        if model not in self.AVAILABLE_MODELS:
            logger.warning(
                f"Modelo '{model}' desconhecido. Usando '{self.DEFAULT_MODEL}'"
            )
            model = self.DEFAULT_MODEL

        self.model_name = model
        self._model = None

    def _load_model(self) -> None:
        """Carrega o modelo Whisper (lazy loading)"""
        if self._model is None:
            logger.info(f"Carregando modelo Whisper '{self.model_name}'...")
            self._model = whisper.load_model(self.model_name)

    def _format_timestamp(self, seconds: float) -> str:
        """
        Formata segundos em timestamp HH:MM:SS

        Args:
            seconds: Tempo em segundos

        Returns:
            String formatada como HH:MM:SS
        """
        return str(timedelta(seconds=int(seconds)))

    def _save_transcript_txt(
        self, transcript: Dict[str, Any], output_path: Path
    ) -> Path:
        """
        Salva o transcript em formato TXT legível com timestamps

        Args:
            transcript: Dicionário com resultado do Whisper
            output_path: Local para salvar o arquivo

        Returns:
            Path do arquivo salvo
        """
        output_file = output_path.with_suffix(".txt")

        with open(output_file, "w", encoding="utf-8") as f:
            # Cabeçalho
            f.write("=" * 70 + "\n")
            f.write("TRANSCRIPT - TRANSCRIÇÃO DO VÍDEO\n")
            f.write("=" * 70 + "\n\n")

            # Idioma detectado
            detected_language = transcript.get("language", "desconhecido")
            f.write(f"Idioma detectado: {detected_language}\n")
            f.write("-" * 70 + "\n\n")

            # Transcrição com timestamps
            f.write("TRANSCRIÇÃO COM TIMESTAMPS:\n")
            f.write("-" * 70 + "\n\n")

            for segment in transcript.get("segments", []):
                start_time = self._format_timestamp(segment["start"])
                end_time = self._format_timestamp(segment["end"])
                text = segment["text"].strip()

                f.write(f"[{start_time} - {end_time}]\n")
                f.write(f"{text}\n\n")

            # Resumo
            f.write("\n" + "=" * 70 + "\n")
            f.write("RESUMO\n")
            f.write("=" * 70 + "\n")

            # Texto completo sem timestamps
            full_text = " ".join(
                [segment["text"] for segment in transcript.get("segments", [])]
            )
            f.write(full_text)

        logger.success(f"Transcript salvo em: {output_file}")
        return output_file

    def _save_transcript_json(
        self, transcript: Dict[str, Any], output_path: Path
    ) -> Path:
        """
        Salva o transcript em formato JSON

        Args:
            transcript: Dicionário com resultado do Whisper
            output_path: Local para salvar o arquivo

        Returns:
            Path do arquivo salvo
        """
        output_file = output_path.with_suffix(".json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON salvo em: {output_file}")
        return output_file

    def transcribe_video(
        self, video_path: Path, output_dir: Optional[Path] = None, language: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Transcreve um vídeo completo

        Args:
            video_path: Path do vídeo
            output_dir: Diretório para salvar o transcript (opcional)
            language: Código de idioma (ex: 'pt' para português, None para auto-detect)

        Returns:
            Dicionário com o resultado ou None se houver erro
        """
        if not video_path.exists():
            logger.error(f"Arquivo não encontrado: {video_path}")
            return None

        try:
            logger.info(f"Iniciando transcrição de: {video_path.name}")
            logger.separator()

            # Carregar modelo
            self._load_model()

            # Transcrever
            logger.info("Transcrevendo áudio (isso pode levar alguns minutos)...")
            result = self._model.transcribe(str(video_path), language=language)

            logger.success("Transcrição concluída!")

            # Determinar diretório de saída
            if output_dir is None:
                output_dir = video_path.parent

            output_dir.mkdir(parents=True, exist_ok=True)

            # Nome do arquivo output
            transcript_name = sanitize_filename(video_path.stem + "_transcript")
            output_path = output_dir / transcript_name

            # Salvar em múltiplos formatos
            logger.separator()
            logger.info("Salvando transcripts...")

            txt_file = self._save_transcript_txt(result, output_path)
            json_file = self._save_transcript_json(result, output_path)

            logger.separator()
            logger.success("Transcrição concluída com sucesso!")

            return result

        except Exception as e:
            logger.error(f"Erro ao transcrever vídeo: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def transcribe_batch(
        self,
        video_paths: list[Path],
        output_dir: Optional[Path] = None,
        language: Optional[str] = None,
    ) -> Dict[str, bool]:
        """
        Transcreve múltiplos vídeos

        Args:
            video_paths: Lista de paths de vídeos
            output_dir: Diretório para salvar os transcripts
            language: Código de idioma

        Returns:
            Dicionário {path: sucesso}
        """
        results = {}

        for i, video_path in enumerate(video_paths, 1):
            logger.info(f"[{i}/{len(video_paths)}] Processando: {video_path.name}")
            logger.separator()

            result = self.transcribe_video(video_path, output_dir, language)
            results[str(video_path)] = result is not None

            logger.separator()

        return results
