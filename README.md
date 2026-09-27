# 🎵 YouTube to MP3 Converter

Convierte videos de YouTube a MP3 con una interfaz web moderna y fácil de usar.

## 🚀 Instalación Rápida

### 1. Instala FFmpeg
```bash
brew install ffmpeg
```

### 2. Instala las dependencias de Python
```bash
cd ~/Desktop/youtube-to-mp3
pip3 install -r requirements.txt
```

## 💻 Uso

### Interfaz Web (Recomendado)

**Opción 1: Usar el script de inicio**
```bash
./run.sh
```

**Opción 2: Ejecutar directamente**
```bash
python3 app.py
```

Luego abre tu navegador en: **http://localhost:3000**

## 🚂 Desplegar en Railway

Este proyecto ya incluye un `Dockerfile` listo para Railway. El contenedor instala FFmpeg, instala las dependencias de Python y arranca Flask con Gunicorn usando el puerto que Railway asigna automáticamente.

### Pasos

1. Sube este proyecto a un repositorio de GitHub.
2. En Railway, crea un proyecto nuevo y elige **Deploy from GitHub repo**.
3. Selecciona este repositorio.
4. Railway detectará el `Dockerfile` y construirá la app.
5. Cuando termine el deploy, entra a **Settings > Networking** y genera un dominio público.

No necesitas configurar variables de entorno para el deploy básico. Railway define `PORT` automáticamente.

### Nota importante

En Railway los archivos no se guardan en tu computadora. Por eso la versión web genera el MP3 temporalmente y lo descarga directamente desde el navegador. Las playlists se descargan como `.zip`.

### Modo Terminal (Alternativo)

Si prefieres usar la terminal:
```bash
python3 youtube_to_mp3.py
```

## 📂 Ubicación de Archivos

Los archivos MP3 se guardan automáticamente en:
```
~/Desktop/Musica_YouTube/
```

## ✨ Características

- 🌐 **Interfaz web moderna y responsive**
- 🎨 **Diseño elegante con gradientes**
- ⚡ **Conversión rápida y sencilla**
- 📥 **Descarga automática al escritorio**
- 🎵 **Calidad de audio: 192 kbps**
- ✅ **Notificaciones en tiempo real**

## 🛠️ Estructura del Proyecto

```
youtube-to-mp3/
├── app.py                 # Aplicación web Flask
├── youtube_to_mp3.py      # Script de línea de comandos
├── run.sh                 # Script de inicio rápido
├── requirements.txt       # Dependencias
├── templates/
│   └── index.html        # Interfaz web
└── README.md             # Este archivo
```

## 📝 Notas

- Asegúrate de tener FFmpeg instalado antes de usar la aplicación
- Los videos muy largos pueden tomar más tiempo en convertirse
- Solo funciona con videos públicos de YouTube
