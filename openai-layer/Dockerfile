# Imagen base oficial de AWS Lambda para Python 3.11
FROM public.ecr.aws/lambda/python:3.11

# Directorio de trabajo
WORKDIR /layer

# Instalar zip (no viene en la imagen base)
RUN yum install -y zip

# Crear estructura requerida para el layer
RUN mkdir -p python

# Instalar la librería OpenAI dentro de la carpeta /layer/python
RUN pip install "openai>=1.0.0" -t python/

# Comprimir la carpeta python en un archivo ZIP listo para subir como Layer
RUN zip -r9 /openai_layer.zip python

# Comando final (solo abre shell si entras manualmente)
CMD ["/bin/bash"]
