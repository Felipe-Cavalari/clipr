"""
Exemplo de uso programático do Clipr
Este arquivo demonstra como usar o Clipr em seus próprios scripts Python
"""

from clipr.downloader import VideoDownloader
from clipr.logger import logger
from clipr.utils import URLValidator


def exemplo_basico():
    """Exemplo básico de download"""
    print("\n=== Exemplo 1: Download Básico ===\n")
    
    downloader = VideoDownloader()
    
    # Baixar um vídeo
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    success = downloader.download(url)
    
    if success:
        print("Download concluído!")
    else:
        print("Falha no download")


def exemplo_com_nome_customizado():
    """Exemplo de download com nome customizado"""
    print("\n=== Exemplo 2: Nome Customizado ===\n")
    
    downloader = VideoDownloader()
    
    url = "https://www.youtube.com/watch?v=VIDEO_ID"
    success = downloader.download(url, custom_filename="meu_video_especial")
    
    return success


def exemplo_obter_informacoes():
    """Exemplo de obtenção de informações sem download"""
    print("\n=== Exemplo 3: Obter Informações ===\n")
    
    downloader = VideoDownloader()
    
    url = "https://www.youtube.com/watch?v=VIDEO_ID"
    info = downloader.get_info(url)
    
    if info:
        print("Informações do vídeo:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        print("Não foi possível obter informações")


def exemplo_validacao_url():
    """Exemplo de validação de URLs"""
    print("\n=== Exemplo 4: Validação de URLs ===\n")
    
    urls_teste = [
        "https://www.youtube.com/watch?v=VIDEO_ID",
        "https://youtube.com/shorts/SHORT_ID",
        "https://www.instagram.com/reel/REEL_ID/",
        "https://site-invalido.com/video",
    ]
    
    for url in urls_teste:
        is_valid, platform = URLValidator.validate_and_identify(url)
        
        if is_valid:
            print(f"✓ URL válida: {url}")
            print(f"  Plataforma: {platform}")
        else:
            print(f"✗ URL inválida: {url}")


def exemplo_download_multiplos():
    """Exemplo de download de múltiplos vídeos"""
    print("\n=== Exemplo 5: Download Múltiplo ===\n")
    
    downloader = VideoDownloader()
    
    urls = [
        "https://www.youtube.com/watch?v=VIDEO_ID_1",
        "https://www.youtube.com/watch?v=VIDEO_ID_2",
        "https://www.instagram.com/reel/REEL_ID/",
    ]
    
    resultados = []
    
    for i, url in enumerate(urls, 1):
        logger.info(f"Baixando {i}/{len(urls)}: {url}")
        success = downloader.download(url)
        resultados.append(success)
    
    # Estatísticas
    sucessos = sum(resultados)
    falhas = len(resultados) - sucessos
    
    print(f"\nResultados:")
    print(f"  Sucessos: {sucessos}")
    print(f"  Falhas: {falhas}")


def exemplo_tratamento_erros():
    """Exemplo de tratamento de erros"""
    print("\n=== Exemplo 6: Tratamento de Erros ===\n")
    
    downloader = VideoDownloader()
    
    # URL inválida
    url_invalida = "https://site-invalido.com/video"
    
    try:
        success = downloader.download(url_invalida)
        if not success:
            print("Download falhou (esperado)")
    except Exception as e:
        print(f"Erro capturado: {e}")


def exemplo_uso_logger():
    """Exemplo de uso do logger"""
    print("\n=== Exemplo 7: Sistema de Logging ===\n")
    
    # Usar o logger diretamente
    logger.header("Título de Seção")
    logger.info("Mensagem informativa")
    logger.success("Operação bem-sucedida")
    logger.warning("Aviso importante")
    logger.error("Erro encontrado")
    logger.debug("Informação de debug")
    logger.separator()


if __name__ == "__main__":
    """
    Execute este arquivo para ver os exemplos em ação:
    python examples.py
    
    Nota: Substitua VIDEO_ID e REEL_ID por IDs reais para testar
    """
    
    print("=" * 60)
    print("CLIPR - Exemplos de Uso Programático")
    print("=" * 60)
    
    # Descomente o exemplo que deseja executar:
    
    # exemplo_basico()
    # exemplo_com_nome_customizado()
    # exemplo_obter_informacoes()
    exemplo_validacao_url()
    # exemplo_download_multiplos()
    # exemplo_tratamento_erros()
    exemplo_uso_logger()
    
    print("\n" + "=" * 60)
    print("Para mais exemplos, veja a documentação no README.md")
    print("=" * 60)
