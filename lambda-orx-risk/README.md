# AWS Lambda Function - Extracción SARO ORX

Esta función Lambda procesa descripciones de eventos SARO y devuelve los riesgos N1 y N2 correspondientes según la taxonomía ORX.

## Estructura del Proyecto

```
lambda-orx-risk/
├── lambda_function.py      # Función Lambda principal
├── extract_n2.py           # Módulo con datos de riesgos ORX
├── requirements_lambda.txt # Dependencias
└── README.md               # Este archivo
```

## Configuración

### AWS Lambda Layer

Esta función requiere una **Lambda Layer** con la librería `openai`. 

**Crear la Layer:**
```bash
# Crear directorio para la layer
mkdir -p layer/python
cd layer/python

# Instalar openai en el directorio python
pip install openai -t .

# Volver al directorio layer
cd ..

# Crear ZIP de la layer
zip -r openai-layer.zip python/

# Crear la layer en AWS
aws lambda publish-layer-version \
  --layer-name openai-layer \
  --zip-file fileb://openai-layer.zip \
  --compatible-runtimes python3.11 python3.12
```

**Asociar la Layer a la función Lambda:**
```bash
aws lambda update-function-configuration \
  --function-name saro-orx-extractor \
  --layers arn:aws:lambda:REGION:ACCOUNT_ID:layer:openai-layer:VERSION
```

### Variables de Entorno

Configura las siguientes variables de entorno en AWS Lambda:

- `OPENAI_API_KEY`: Tu API key de OpenAI (requerida)

### Permisos IAM

La función Lambda necesita permisos para:
- Acceso a internet (para llamar a la API de OpenAI)

## Despliegue

### Opción 1: Usando AWS CLI

1. **Crear un paquete de despliegue:**

```bash
# Desde el directorio lambda-orx-risk
cd lambda-orx-risk

# Crear directorio para el paquete
mkdir -p package
cd package

# Copiar archivos necesarios
cp ../lambda_function.py .
cp ../extract_n2.py .

# NO instalar dependencias aquí - estarán en la Layer
# Las dependencias (openai) deben estar en una Lambda Layer

# Crear ZIP
zip -r ../lambda_function.zip .
cd ..
```

2. **Crear la función Lambda:**

```bash
aws lambda create-function \
  --function-name saro-orx-extractor \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{OPENAI_API_KEY=tu-api-key}"
```

3. **Actualizar la función:**

```bash
aws lambda update-function-code \
  --function-name saro-orx-extractor \
  --zip-file fileb://lambda_function.zip
```

### Opción 2: Usando AWS SAM

1. **Crear `template.yaml`:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  SaroOrxExtractor:
    Type: AWS::Serverless::Function
    Properties:
      Handler: lambda_function.lambda_handler
      Runtime: python3.11
      CodeUri: .
      Timeout: 300
      MemorySize: 512
      Environment:
        Variables:
          OPENAI_API_KEY: !Ref OpenAIApiKey
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /saro
            Method: post
```

2. **Desplegar:**

```bash
sam build
sam deploy --guided
```

## Uso con API Gateway

### Request Body

```json
{
  "descripcion": "La tesoreria del banco no pudo operar durante 3 horas porque los enlaces de comunicaciones se cayeron por un incendio en la camara de comunicaciones."
}
```

### Response

```json
{
  "statusCode": 200,
  "body": {
    "eventos_n1": [
      "Tecnología",
      "Continuidad del negocio"
    ],
    "riesgos": [
      {
        "Riesgo_nivel_1": "Tecnología",
        "Riesgo_nivel_2": [
          "Fallo de red"
        ]
      },
      {
        "Riesgo_nivel_1": "Continuidad del negocio",
        "Riesgo_nivel_2": [
          "Planificación de continuidad empresarial/gestión de eventos inadecuada"
        ]
      }
    ]
  }
}
```

## Parámetros Opcionales

- `model`: Modelo de OpenAI a usar (default: "gpt-4o-mini")
  - Opciones: "gpt-4o-mini", "gpt-4o", "gpt-4-turbo", etc.

Ejemplo:

```json
{
  "descripcion": "Evento SARO...",
  "model": "gpt-4o"
}
```

## Límites y Consideraciones

- **Timeout**: Configurado a 300 segundos (5 minutos) para permitir múltiples llamadas a OpenAI
- **Memory**: 512 MB recomendado
- **Cold Start**: La primera invocación puede tardar más debido a la carga de dependencias
- **Costo**: Cada invocación realiza múltiples llamadas a OpenAI (una para N1 y una por cada N1 para filtrar N2)

## Testing Local

Puedes probar la función localmente:

```python
import json
from lambda_function import lambda_handler

event = {
    'body': json.dumps({
        'descripcion': 'La tesoreria del banco no pudo operar durante 3 horas...'
    })
}

result = lambda_handler(event, None)
print(json.dumps(json.loads(result['body']), indent=2))
```

## Troubleshooting

### Error: "OPENAI_API_KEY no está configurada"
- Verifica que la variable de entorno esté configurada en Lambda
- Asegúrate de que el valor no tenga espacios extra

### Error: "Timeout"
- Aumenta el timeout de la función Lambda
- Considera usar un modelo más rápido (gpt-4o-mini)

### Error: "Memory limit exceeded"
- Aumenta el memory size de la función Lambda
- 512 MB debería ser suficiente, pero puedes aumentar a 1024 MB si es necesario

