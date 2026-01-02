#!/bin/bash

# Script para desarrollo local con hot-reload

set -e

echo "🚀 Iniciando entorno de desarrollo DIVIPOLA API..."

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# Función para limpiar al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    docker-compose -f docker-compose.dev.yml down
    exit 0
}

trap cleanup SIGINT SIGTERM

# Construir y levantar servicios
echo "📦 Construyendo imágenes..."
docker-compose -f docker-compose.dev.yml build

echo "🔧 Levantando servicios..."
docker-compose -f docker-compose.dev.yml up

