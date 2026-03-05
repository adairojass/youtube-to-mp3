#!/usr/bin/env python3
"""
YouTube to MP3 Converter
Descarga videos de YouTube y los convierte a MP3
"""

import os
import sys
from pathlib import Path
import yt_dlp


def get_desktop_path():
    """Obtiene la ruta del escritorio del usuario"""
    return str(Path.home() / "Desktop" / "Musica_YouTube")


def download_youtube_to_mp3(url, output_folder=None):
    """
    Descarga un video de YouTube y lo convierte a MP3
    
    Args:
        url: URL del video de YouTube
        output_folder: Carpeta de destino (por defecto: Desktop/Musica_YouTube)
    """
    if output_folder is None:
        output_folder = get_desktop_path()
    
    # Crear la carpeta si no existe
    os.makedirs(output_folder, exist_ok=True)
    
    # Configuración de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
        ],
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'noplaylist': True,
        'writethumbnail': False,
        'add_metadata': True,
        'postprocessor_args': {
            'FFmpegMetadata': ['-metadata', 'artist=%(uploader)s', '-metadata', 'title=%(title)s']
        },
    }
    
    try:
        print(f"\n🎵 Descargando desde: {url}")
        print(f"📁 Guardando en: {output_folder}\n")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            print(f"\n✅ ¡Descarga completada! {title}")
            
    except Exception as e:
        print(f"\n❌ Error al descargar: {str(e)}")
        return False
    
    return True


def main():
    """Función principal"""
    print("=" * 60)
    print("🎵  YouTube to MP3 Converter  🎵")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # URL proporcionada como argumento
        url = sys.argv[1]
        output_folder = sys.argv[2] if len(sys.argv) > 2 else None
        download_youtube_to_mp3(url, output_folder)
    else:
        # Modo interactivo
        print("\nPega la URL del video de YouTube que quieres convertir:")
        url = input("URL: ").strip()
        
        if not url:
            print("❌ No se proporcionó ninguna URL")
            return
        
        print(f"\n¿Dónde quieres guardar el archivo?")
        print(f"(Presiona Enter para usar: {get_desktop_path()})")
        custom_folder = input("Ruta: ").strip()
        
        output_folder = custom_folder if custom_folder else None
        download_youtube_to_mp3(url, output_folder)
        
        # Preguntar si quiere descargar otro
        print("\n" + "=" * 60)
        while True:
            resp = input("\n¿Descargar otro video? (s/n): ").strip().lower()
            if resp == 'n':
                break
            elif resp == 's':
                url = input("URL: ").strip()
                if url:
                    download_youtube_to_mp3(url, output_folder)
            else:
                print("Responde 's' para sí o 'n' para no")


if __name__ == "__main__":
    main()
