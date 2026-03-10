# Clipr - Guia de Uso Rápido

## Instalação Rápida

```powershell
# 1. Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar Clipr
pip install -e .

# 4. Testar instalação
clipr test
```

```bash
# macOS / Linux
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar Clipr
pip install -e .

# 4. Testar instalação
clipr test
```

## Comandos Essenciais

### Download básico

```bash
clipr download <URL>
```

### Download em lote

```bash
clipr batch URL1 URL2 URL3
```

### Ver informações

```bash
clipr download <URL> --info
```

### Ajuda

```bash
clipr --help
clipr download --help
```

## Plataformas Suportadas

✅ YouTube (vídeos e Shorts)
✅ Instagram (Reels)

## Qualidade de Download

- **YouTube horizontal**: 1920x1080 (Full HD)
- **YouTube Shorts**: 1080x1920 (vertical)
- **Instagram Reels**: Melhor qualidade disponível

## Onde os vídeos são salvos?

```
C:\Users\felip\Videos\Videos baixados\
├── Youtube\
└── Instagram\
```

```text
/Users/<seu_usuario>/Movies/Videos baixados/
├── Youtube/
└── Instagram/
```

Também é possível customizar o diretório base com `CLIPR_OUTPUT_DIR`.

## Requisitos

- Python 3.10+
- FFmpeg (obrigatório)

### Instalar FFmpeg

```powershell
choco install ffmpeg
```

```bash
brew install ffmpeg
```

## Exemplos Práticos

```bash
# Baixar vídeo do YouTube
clipr download https://www.youtube.com/watch?v=VIDEO_ID

# Baixar Short
clipr download https://youtube.com/shorts/SHORT_ID

# Baixar Reel do Instagram
clipr download https://www.instagram.com/reel/REEL_ID/

# Com nome customizado
clipr download URL --name "meu_video"

# Múltiplos vídeos
clipr batch URL1 URL2 URL3 --continue-on-error
```

## Suporte

Issues: https://github.com/CavalariDev/clipr/issues
