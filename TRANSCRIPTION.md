# Transcrição de Vídeos - Clipr

## 🎯 Visão Geral

A feature de **Transcrição de Vídeos** do Clipr utiliza o modelo **Whisper** da OpenAI para gerar transcritos automáticos de vídeos baixados do YouTube e Instagram.

Os transcritos são salvos em **dois formatos**:

1. **TXT** - Formato legível com timestamps (HH:MM:SS)
2. **JSON** - Formato estruturado com metadados completos

## 📋 Como Usar

### 1. Transcrever durante o Download

Adicione a flag `--transcribe` ao comando de download:

```bash
# Download com transcrição automática
clipr download https://www.youtube.com/watch?v=VIDEO_ID --transcribe

# Especificar modelo Whisper (padrão: base)
clipr download URL --transcribe --model small

# Download com nome customizado e transcrição
clipr download URL --name "meu_video" --transcribe
```

### 2. Transcrever Vídeos Já Baixados

Use o comando `transcribe` para processar vídeos já salvos:

```bash
# Transcrever um arquivo específico
clipr transcribe ~/Movies/Videos\ baixados/Youtube/video.mp4

# Transcrever todos os vídeos de um diretório
clipr transcribe ~/Movies/Videos\ baixados/Youtube/

# Especificar modelo Whisper
clipr transcribe video.mp4 --model small

# Especificar idioma (ex: português)
clipr transcribe video.mp4 --language pt
```

## 🔧 Modelos Disponíveis

| Modelo   | Tamanho  | Velocidade   | Qualidade |
| -------- | -------- | ------------ | --------- |
| `tiny`   | ~39 MB   | Muito Rápido | Básica    |
| `base`   | ~74 MB   | Rápido       | Boa       |
| `small`  | ~244 MB  | Médio        | Muito Boa |
| `medium` | ~769 MB  | Lento        | Excelente |
| `large`  | ~1550 MB | Muito Lento  | Melhor    |

**Padrão:** `base` (bom balanço entre velocidade e qualidade)

## 📂 Estrutura de Arquivos

Os transcritos são salvos organizados por plataforma:

```
~/Movies/Videos baixados/
├── Youtube/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── Transcripts/
│       ├── video1_transcript.txt
│       ├── video1_transcript.json
│       ├── video2_transcript.txt
│       └── video2_transcript.json
│
└── Instagram/
    ├── reel1.mp4
    ├── reel2.mp4
    └── Transcripts/
        ├── reel1_transcript.txt
        ├── reel1_transcript.json
        ├── reel2_transcript.txt
        └── reel2_transcript.json
```

## 📝 Formato TXT

Os arquivos TXT contêm uma formatação legível com:

```
======================================================================
TRANSCRIPT - TRANSCRIÇÃO DO VÍDEO
======================================================================

Idioma detectado: Portuguese

----------------------------------------------------------------------

TRANSCRIÇÃO COM TIMESTAMPS:

----------------------------------------------------------------------

[00:00:05 - 00:00:12]
Este é um exemplo de transcrição automática.

[00:00:12 - 00:00:20]
O Whisper detecta automaticamente o idioma do áudio.

[00:00:20 - 00:00:45]
E gera timestamps para cada segmento da fala.

======================================================================
RESUMO
======================================================================

Este é um exemplo de transcrição automática. O Whisper detecta automaticamente o idioma do áudio. E gera timestamps para cada segmento da fala.
```

## 🌐 Idiomas Suportados

Whisper suporta transcrição em mais de 90 idiomas, incluindo:

- Portuguese (Português): `pt`
- English: `en`
- Spanish: `es`
- French: `fr`
- German: `de`
- E muitos outros!

Para especificar um idioma:

```bash
clipr transcribe video.mp4 --language pt
```

## ⚙️ Requisitos

### Dependências Python

- `openai-whisper` - Engine de transcrição
- `pydub` - Processamento de áudio
- `torch` - Framework de deep learning

### Dependências Externas

- **FFmpeg** - Necessário para extrair áudio do vídeo

#### Instalar FFmpeg

**macOS:**

```bash
brew install ffmpeg
```

**Windows (Chocolatey):**

```powershell
choco install ffmpeg
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install ffmpeg
```

## 🚀 Exemplos Práticos

### Exemplo 1: Transcrever YouTube com modelo rápido

```bash
clipr download https://www.youtube.com/watch?v=abc123 \
  --name "minha_aula" \
  --transcribe \
  --model tiny
```

### Exemplo 2: Transcrever lote de vídeos em português

```bash
clipr transcribe ~/Movies/Videos\ baixados/Youtube/ --language pt --model base
```

### Exemplo 3: Transcrever com máxima qualidade (mas lento)

```bash
clipr transcribe video.mp4 --model large
```

## 📊 Casos de Uso

- **📚 Educação**: Converter aulas em vídeo para texto
- **🎙️ Podcasts**: Transcrever episódios de vídeo
- **📰 Jornalismo**: Arquivar conteúdo em texto
- **🤖 IA/ML**: Processamento de linguagem natural
- **♿ Acessibilidade**: Legendas para vídeos sem áudio
- **🔍 SEO**: Indexar conteúdo de vídeo

## ⚠️ Notas Importantes

1. **Tempo de Processamento**: A transcrição pode levar algum tempo dependendo:
   - Duração do vídeo
   - Modelo Whisper escolhido
   - Poder de processamento da máquina

2. **Qualidade de Áudio**: Áudios de melhor qualidade resultam em transcritos mais precisos

3. **Memória**: Modelos maiores (medium, large) requerem mais RAM

4. **Primeira Execução**: Na primeira vez que você usa um modelo, o Whisper baixa o modelo (~40MB a 1.5GB)

## 🔥 Dicas e Boas Práticas

- Use `tiny` ou `base` para processamento rápido
- Use `small` para bom balanço
- Use `medium` ou `large` para máxima qualidade
- Execute durante períodos de inatividade para não impactar outro uso do computador
- Certifique-se de ter espaço em disco livre para os arquivos

## 🐛 Troubleshooting

### Erro: "Whisper não encontrado"

```bash
pip install openai-whisper
```

### Erro: "FFmpeg não encontrado"

Instale FFmpeg conforme as instruções acima para seu sistema operacional.

### A transcrição está muito lenta

Tente usar um modelo menor:

```bash
clipr transcribe video.mp4 --model tiny
```

### Qualidade ruim do transcript

Tente usar um modelo maior:

```bash
clipr transcribe video.mp4 --model large
```

## 📚 Referências

- [OpenAI Whisper GitHub](https://github.com/openai/whisper)
- [Documentação Whisper](https://github.com/openai/whisper/blob/main/README.md)
- [Modelos e Linguagens Suportadas](https://github.com/openai/whisper/blob/main/README.md#available-models-and-languages)
