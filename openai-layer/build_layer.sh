#!/bin/bash

set -euo pipefail

ROOT_DIR="/Users/johanemiliopaezjimenez/Davivienda Workspace/orx-lambdas/openai-layer"
PYTHON_DIR="$ROOT_DIR/python"
ZIP_FILE="$ROOT_DIR/openai-layer.zip"
ZIP_NAME="$(basename "$ZIP_FILE")"

IMAGE="public.ecr.aws/lambda/python:3.11"

echo "Limpiando directorio python..."
rm -rf "$PYTHON_DIR"/*
mkdir -p "$PYTHON_DIR"
rm -f "$ZIP_FILE"

echo "Instalando dependencias dentro de Docker ($IMAGE)..."
docker run --rm \
  -v "$ROOT_DIR":/var/task \
  --entrypoint /bin/bash \
  "$IMAGE" \
  -c "pip install -r requirements.txt -t python"

echo "Empaquetando layer en $ZIP_FILE..."
docker run --rm \
  -v "$ROOT_DIR":/var/task \
  --entrypoint /bin/bash \
  "$IMAGE" \
  -c "cd /var/task && python -m zipfile -c '$ZIP_NAME' python"

echo "Layer creada: $ZIP_FILE"

