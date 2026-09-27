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
import webbrowser
import threading
import zipfile
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)

def get_desktop_path():
    """Obtiene la ruta del escritorio del usuario"""
    return str(Path.home() / "Desktop" / "Musica_YouTube")

def clean_title(title):
    """Limpia el título removiendo patrones de artista al inicio"""
    # Remover patrones como "Artista - " o "Artista: " al inicio
    cleaned = re.sub(r'^[^-:]+[-:]\s*', '', title)
    return cleaned.strip() if cleaned else title

def safe_download_name(name, extension):
    """Crea un nombre de archivo seguro para enviar al navegador."""
    cleaned = secure_filename(clean_title(name)) or "audio"
    return f"{cleaned}.{extension}"

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
            filepath = os.path.splitext(ydl.prepare_filename(info))[0] + '.mp3'
            
            # Limpiar el nombre del archivo
            clean_name = clean_title(title)
            new_filepath = os.path.join(output_folder, safe_download_name(clean_name, 'mp3'))
            
            # Renombrar el archivo si existe
            if os.path.exists(filepath) and filepath != new_filepath:
                os.rename(filepath, new_filepath)
                filepath = new_filepath
            
            return {
                'success': True,
                'title': clean_name,
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'message': f'¡Descarga completada! {clean_name}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al descargar: {str(e)}'
        }

def download_playlist_to_mp3(url, output_folder=None):
    """
    Descarga una playlist completa de YouTube y convierte todos los videos a MP3
    
    Args:
        url: URL de la playlist de YouTube
        output_folder: Carpeta de destino
    
    Returns:
        dict: Información de los archivos descargados o error
    """
    if output_folder is None:
        output_folder = get_desktop_path()
    
    # Crear la carpeta si no existe
    os.makedirs(output_folder, exist_ok=True)
    
    # Configuración de yt-dlp para playlists
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
        'outtmpl': os.path.join(output_folder, '%(playlist)s', '%(playlist_index)s - %(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': False,  # Permitir playlists
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
            
            # Verificar si es una playlist
            if 'entries' in info:
                playlist_title = info.get('title', 'Playlist')
                total_videos = len(info['entries'])
                
                return {
                    'success': True,
                    'playlist_title': playlist_title,
                    'total_videos': total_videos,
                    'output_folder': output_folder,
                    'message': f'¡Playlist descargada! {playlist_title} - {total_videos} canciones'
                }
            else:
                # Si no es una playlist, descargar como canción individual
                title = info.get('title', 'Unknown')
                return {
                    'success': True,
                    'title': title,
                    'message': f'¡Descarga completada! {title}'
                }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error al descargar playlist: {str(e)}'
        }

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Endpoint simple para verificar que el servicio está vivo."""
    return jsonify({'status': 'ok'})

def file_response(filepath, download_name):
    """Lee el archivo en memoria para poder borrar temporales al terminar."""
    buffer = BytesIO(Path(filepath).read_bytes())
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=download_name)

def zip_folder_response(folder, download_name):
    """Empaqueta los MP3 generados para descargar playlists desde el navegador."""
    buffer = BytesIO()
    mp3_files = sorted(Path(folder).rglob('*.mp3'))

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for mp3_file in mp3_files:
            archive.write(mp3_file, mp3_file.relative_to(folder))

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/zip',
    )

@app.route('/convert', methods=['POST'])
def convert():
    """Endpoint para convertir video a MP3"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        download_type = data.get('type', 'single')  # 'single' o 'playlist'
        
        if not url:
            return jsonify({
                'success': False,
                'message': 'Por favor ingresa una URL válida'
            }), 400
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Descargar según el tipo seleccionado
            if download_type == 'playlist':
                result = download_playlist_to_mp3(url, temp_dir)
                if not result.get('success'):
                    return jsonify(result), 400

                download_name = safe_download_name(result.get('playlist_title', 'playlist'), 'zip')
                return zip_folder_response(temp_dir, download_name)

            result = download_youtube_to_mp3(url, temp_dir)

            if not result.get('success'):
                return jsonify(result), 400

            return file_response(
                result['filepath'],
                result.get('filename') or safe_download_name(result.get('title', 'audio'), 'mp3')
            )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

def open_browser():
    """Abre el navegador automáticamente"""
    webbrowser.open('http://localhost:3000')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    print("\n" + "="*60)
    print("🎵  YouTube to MP3 Converter - Interfaz Web  🎵")
    print("="*60)
    print("\n✨ Servidor iniciado correctamente")
    print("\n🌐 Servidor escuchando en:", f"http://0.0.0.0:{port}")
    print("\n⚠️  Presiona Ctrl+C para detener el servidor\n")
    
    if not os.environ.get('PORT'):
        # Abrir el navegador solo cuando se ejecuta localmente.
        threading.Timer(1.5, open_browser).start()
    
    app.run(debug=debug, host='0.0.0.0', port=port)
