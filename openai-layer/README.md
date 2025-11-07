OpenAI Lambda Layer
====================

Este directorio contiene los archivos necesarios para construir una AWS Lambda Layer que provea la librería `openai` a las funciones Lambda.

Estructura
----------

```
openai-layer/
├── README.md
├── requirements.txt
├── build_layer.sh
└── python/              # Destino donde `pip` instalará las dependencias
```

Pasos de construcción
---------------------

1. **Instalar dependencias dentro del directorio `python/`:**

   ```bash
   cd /Users/johanemiliopaezjimenez/Davivienda\ Workspace/orx-lambdas/openai-layer
   pip install -r requirements.txt -t python
   ```

   Esto descargará la librería `openai` y sus dependencias dentro de `python/`.

2. **Empaquetar la layer:**

   ```bash
   zip -r openai-layer.zip python
   ```

3. **Publicar la layer en AWS:**

   ```bash
   aws lambda publish-layer-version \
     --layer-name openai-layer \
     --zip-file fileb://openai-layer.zip \
     --compatible-runtimes python3.11 python3.12
   ```

4. **Asociar la layer a la función Lambda:**

   ```bash
   aws lambda update-function-configuration \
     --function-name TU_FUNCION_LAMBDA \
     --layers arn:aws:lambda:REGION:ACCOUNT_ID:layer:openai-layer:VERSION
   ```

Reconstrucción limpia
---------------------

Para regenerar la layer desde cero:

```bash
rm -rf python/*
pip install -r requirements.txt -t python
zip -r openai-layer.zip python
```

Notas
-----

- Ajusta la versión de la librería `openai` en `requirements.txt` según tus necesidades.
- El directorio `python/` debe mantenerse en el control de versiones vacío (solo contiene dependencias instaladas); puedes usar un `.gitignore` para excluir su contenido.
- Si necesitas soporte para más runtimes, agrégalos al comando `--compatible-runtimes`.

