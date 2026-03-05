#!/usr/bin/env python3
"""
YouTube to MP3 Converter - Interfaz Web
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import sys
import re
from pathlib import Path
import yt_dlp
import tempfile
import time

app = Flask(__name__)

def get_desktop_path():
    """Obtiene la ruta del escritorio del usuario"""
    return str(Path.home() / "Desktop" / "Musica_YouTube")

def clean_title(title):
    """Limpia el título removiendo patrones de artista al inicio"""
    # Remover patrones como "Artista - " o "Artista: " al inicio
    cleaned = re.sub(r'^[^-:]+[-:]\s*', '', title)
    return cleaned.strip() if cleaned else title

def download_youtube_to_mp3(url, output_folder=None):
    """
    Descarga un video de YouTube y lo convierte a MP3
    
    Args:
        url: URL del video de YouTube
        output_folder: Carpeta de destino
    
    Returns:
        dict: Información del archivo descargado o error
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
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
        'nocheckcertificate': True,
        'writethumbnail': False,
        'add_metadata': True,
        'postprocessor_args': {
            'FFmpegMetadata': ['-metadata', 'artist=%(uploader)s', '-metadata', 'title=%(title)s']
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            filename = f"{title}.mp3"
            filepath = os.path.join(output_folder, filename)
            
            # Limpiar el nombre del archivo
            clean_name = clean_title(title)
            new_filepath = os.path.join(output_folder, f"{clean_name}.mp3")
            
            # Renombrar el archivo si existe
            if os.path.exists(filepath) and filepath != new_filepath:
                os.rename(filepath, new_filepath)
                filepath = new_filepath
            
            return {
                'success': True,
                'title': clean_name,
                'filepath': filepath,
                'message': f'¡Descarga completada! {clean_name}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al descargar: {str(e)}'
        }

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """Endpoint para convertir video a MP3"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'message': 'Por favor ingresa una URL válida'
            }), 400
        
        # Descargar y convertir
        result = download_youtube_to_mp3(url)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎵  YouTube to MP3 Converter - Interfaz Web  🎵")
    print("="*60)
    print("\n✨ Servidor iniciado correctamente")
    print("📂 Los archivos se guardarán en:", get_desktop_path())
    print("\n🌐 Abre tu navegador en: http://localhost:3000")
    print("\n⚠️  Presiona Ctrl+C para detener el servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=3000)
