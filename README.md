# Clipr 🎬

**Ferramenta CLI profissional para download de vídeos do YouTube e Instagram Reels**

Clipr é uma ferramenta de linha de comando robusta e fácil de usar para baixar vídeos do YouTube (incluindo Shorts) e Instagram Reels com qualidade máxima e organização automática.

---

## ✨ Características

- 🎯 **Detecção automática de plataforma** - Identifica YouTube ou Instagram pela URL
- 📺 **Otimização de qualidade**:
  - Vídeos horizontais do YouTube → 1920x1080 (Full HD)
  - Shorts do YouTube → 1080x1920 (qualidade vertical)
  - Instagram Reels → Melhor qualidade disponível
- 📁 **Organização automática** - Separa vídeos por plataforma
- 🚫 **Prevenção de duplicatas** - Evita baixar vídeos já existentes
- 💪 **Tratamento robusto de erros** - Mensagens claras e informativas
- 🎨 **Interface bonita e informativa** - Logs coloridos com Rich
- ⚡ **Download em lote** - Baixe múltiplos vídeos de uma vez
- ✂️ **Corte interativo de vídeo** - Defina pontos de início/fim no terminal, com suporte a múltiplos cortes e concatenação automática

---

## 📋 Requisitos

- **Python 3.10+**
- **FFmpeg** (necessário para mesclar áudio e vídeo)

### Instalar FFmpeg no macOS

```bash
# Usando Homebrew
brew install ffmpeg
```

### Instalar FFmpeg no Windows

```powershell
# Usando Chocolatey
choco install ffmpeg

# Ou baixe manualmente de: https://ffmpeg.org/download.html
```

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/CavalariDev/clipr.git
cd clipr
```

### 2. Crie um ambiente virtual (recomendado)

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Instale o Clipr

```bash
pip install -e .
```

---

## 📖 Uso

### Comando básico

```bash
clipr download <URL>
```

### Exemplos práticos

#### Baixar um vídeo do YouTube

```bash
clipr download https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

#### Baixar um Short do YouTube

```bash
clipr download https://youtube.com/shorts/AbCdEfGhIjK
```

#### Baixar um Reel do Instagram

```bash
clipr download https://www.instagram.com/reel/AbCdEfGhIjK/
```

#### Baixar somente o áudio em mp3

```bash
clipr download https://www.youtube.com/watch?v=dQw4w9WgXcQ --audio-only
```

#### Baixar com nome customizado

```bash
clipr download https://youtube.com/watch?v=VIDEO_ID --name "meu_video"
```

#### Ver informações sem baixar

```bash
clipr download https://youtube.com/watch?v=VIDEO_ID --info
```

#### Download em lote

```bash
clipr batch URL1 URL2 URL3
```

#### Download em lote continuando mesmo com erros

```bash
clipr batch URL1 URL2 URL3 --continue-on-error
```

---

## ✂️ Corte Interativo de Vídeo (`clipr trim`)

O comando `trim` permite cortar vídeos diretamente pelo terminal com uma experiência interativa.
Aceita tanto arquivos locais quanto URLs (YouTube, Instagram, TikTok).

### Uso básico

```bash
clipr trim video.mp4
clipr trim https://youtube.com/watch?v=VIDEO_ID
clipr trim video.mp4 --output corte_final.mp4
```

### Flags disponíveis

| Flag | Atalho | Descrição |
|---|---|---|
| `--output` | `-o` | Nome do arquivo de saída (padrão: `<nome>_trimmed.mp4`) |
| `--format` | | Formato de saída: `mp4` (padrão), `mkv`, `mov`, `avi` |
| `--browser` | `-b` | Browser para cookies ao baixar URL (ex: `chrome`, `firefox`) |

### Fluxo interativo

1. Clipr exibe a duração e resolução do vídeo
2. Você define os pontos de **início** e **fim** de cada corte (formatos aceitos: `HH:MM:SS`, `MM:SS` ou segundos inteiros)
3. Uma tabela mostra os cortes adicionados com a duração resultante
4. Escolha se quer adicionar mais cortes, desfazer o último ou finalizar
5. O FFmpeg processa os cortes sem re-encode (`-c copy`) para máxima velocidade
6. Se houver múltiplos cortes, os segmentos são automaticamente concatenados

### Exemplos

```bash
# Arquivo local — corte único
clipr trim video.mp4

# URL do YouTube com nome de saída customizado
clipr trim https://youtube.com/watch?v=XYZ --output destaque.mp4

# Arquivo com formato MKV
clipr trim video.mp4 --format mkv

# URL com cookies do Chrome (vídeos com restrição de idade)
clipr trim https://youtube.com/watch?v=XYZ --browser chrome
```

---

### Outros comandos úteis

#### Ver caminhos de saída

```bash
clipr paths
```

#### Testar instalação

```bash
clipr test
```

#### Ver ajuda

```bash
clipr --help
clipr download --help
clipr batch --help
```

---

## 📂 Estrutura de Pastas

Os vídeos são salvos automaticamente em (diretório padrão por sistema):

```
C:\Users\felip\Videos\Videos baixados\
├── Youtube\       # Vídeos e Shorts do YouTube
└── Instagram\     # Reels do Instagram
```

```text
/Users/<seu_usuario>/Movies/Videos baixados/
├── Youtube/        # Vídeos e Shorts do YouTube
└── Instagram/      # Reels do Instagram
```

Também é possível customizar o diretório base com a variável de ambiente `CLIPR_OUTPUT_DIR`.

---

## 🏗️ Arquitetura do Projeto

```
clipr/
├── clipr/
│   ├── __init__.py      # Inicialização do pacote
│   ├── cli.py           # Interface CLI (Click)
│   ├── downloader.py    # Gerenciador unificado
│   ├── youtube.py       # Downloader do YouTube
│   ├── instagram.py     # Downloader do Instagram
│   ├── tiktok.py        # Downloader do TikTok
│   ├── trimmer.py       # Corte interativo de vídeo (FFmpeg)
│   ├── transcriber.py   # Transcrição com Whisper
│   ├── utils.py         # Utilitários e validações
│   └── logger.py        # Sistema de logging (Rich)
├── requirements.txt     # Dependências
├── setup.py            # Configuração de instalação
└── README.md           # Este arquivo
```

### Módulos

- **`cli.py`** - Interface de linha de comando usando Click
- **`downloader.py`** - Orquestrador que detecta a plataforma e delega o download
- **`youtube.py`** - Lógica específica para YouTube (vídeos e Shorts)
- **`instagram.py`** - Lógica específica para Instagram Reels
- **`tiktok.py`** - Lógica específica para TikTok
- **`trimmer.py`** - Corte interativo de vídeo com FFmpeg (ffprobe, loop interativo, concat)
- **`transcriber.py`** - Transcrição automática via Whisper
- **`utils.py`** - Validação de URLs, sanitização de nomes, gerenciamento de paths
- **`logger.py`** - Sistema de logging com Rich para saída bonita no terminal

---

## 🔧 Desenvolvimento

### Estrutura modular

O código foi projetado para ser facilmente extensível:

- Adicionar novas plataformas: crie um novo downloader em `clipr/nova_plataforma.py`
- Adicionar novos recursos: implemente em módulos separados
- Testes: adicione testes em `tests/`

### Boas práticas implementadas

✅ Type hints em todas as funções  
✅ Docstrings detalhadas  
✅ Tratamento de erros específico  
✅ Separação de responsabilidades  
✅ Código limpo e legível  
✅ Validações robustas

---

## ❌ Tratamento de Erros

Clipr trata diversos tipos de erro graciosamente:

- 🔗 **URL inválida** - Valida formato e plataforma
- 🔒 **Vídeo privado** - Detecta e informa claramente
- 🚫 **Vídeo indisponível** - Identifica conteúdo removido
- 🌐 **Falha de rede** - Tratamento de timeouts e conexões
- 📉 **Resolução não disponível** - Seleciona melhor alternativa
- 💾 **Espaço em disco** - Verifica antes de baixar
- ⚠️ **FFmpeg ausente** - Avisa sobre dependências

---

## 🛠️ Solução de Problemas

### FFmpeg não encontrado

Se receber erro sobre FFmpeg:

1. Instale o FFmpeg (veja seção Requisitos)
2. Adicione ao PATH do sistema
3. Reinicie o terminal

### Vídeo privado ou restrito

Certifique-se de que:

- O vídeo é público
- A URL está correta
- O conteúdo não foi removido

### Erro de rede

Verifique sua conexão e tente novamente. Use a opção `--continue-on-error` para lotes.

---

## 📝 Licença

MIT License - Sinta-se livre para usar, modificar e distribuir.

---

## 👨‍💻 Autor

**Felipe Cavalari**

- GitHub: [@CavalariDev](https://github.com/CavalariDev)

---

## 🙏 Agradecimentos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Biblioteca poderosa para download de vídeos
- [Click](https://click.palletsprojects.com/) - Framework para CLI
- [Rich](https://github.com/Textualize/rich) - Interface bonita para terminal

---

## 🚀 Roadmap

Recursos planejados para versões futuras:

- ✅ Suporte para TikTok
- ✅ Corte interativo de vídeo (`clipr trim`)
- ✅ Transcrição automática com Whisper
- [ ] Downloads paralelos
- [ ] Playlist completa
- [ ] Conversão automática para diferentes formatos
- [ ] Extração de legendas
- [ ] Interface web
- [ ] Configuração via arquivo
- [ ] Agendamento de downloads

---

## 📞 Suporte

Para bugs, sugestões ou dúvidas:

- Abra uma [issue no GitHub](https://github.com/CavalariDev/clipr/issues)
- Entre em contato via [LinkedIn](https://linkedin.com/in/felipecavalari)

---

**Feito com ❤️ e Python**
