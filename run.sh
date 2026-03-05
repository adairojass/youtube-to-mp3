#!/bin/bash

echo "🎵 Iniciando YouTube to MP3 Converter..."
echo ""

# Verificar si FFmpeg está instalado
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg no está instalado. Por favor instálalo con:"
    echo "   brew install ffmpeg"
    echo ""
    exit 1
fi

# Ejecutar la aplicación
python3 app.py
