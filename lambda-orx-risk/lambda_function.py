import json
import re
import os
from typing import Dict, Any, List

# AWS Lambda automáticamente agrega las capas al sys.path cuando están asociadas
# Las capas se montan en /opt/python/lib/python3.x/site-packages/ y se agregan automáticamente
try:
    from openai import OpenAI
except ImportError as e:
    raise ImportError(
        "No se pudo importar openai. Asegúrate de que la Lambda Layer con openai esté configurada "
        "y asociada a la función Lambda, o que openai esté instalado en el entorno local. Error: " + str(e)
    )

# Importar datos y funciones de extract_n2
from extract_n2 import RIESGOS_ORX_DATA, normalize_n1_name


def get_riesgos_n2_por_n1(n1_list: List[str], riesgos_data: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """
    Obtiene todos los riesgos N2 posibles agrupados por su N1 correspondiente.
    """
    riesgos_por_n1 = {}
    n1_normalized = {normalize_n1_name(n1): n1 for n1 in n1_list}
    
    # Agrupar riesgos N2 por N1
    for riesgo in riesgos_data:
        riesgo_n1_json = riesgo.get("Riesgo_nivel_1", "")
        riesgo_n2 = riesgo.get("Riesgo_nivel_2", "")
        
        # Buscar si este N1 está en la lista normalizada
        n1_original = None
        for n1_norm, n1_orig in n1_normalized.items():
            if n1_norm == riesgo_n1_json:
                n1_original = n1_orig
                break
        
        if n1_original and riesgo_n2:
            if n1_original not in riesgos_por_n1:
                riesgos_por_n1[n1_original] = []
            if riesgo_n2 not in riesgos_por_n1[n1_original]:
                riesgos_por_n1[n1_original].append(riesgo_n2)
    
    return riesgos_por_n1


def get_openai_client() -> OpenAI:
    """Inicializa el cliente de OpenAI usando variables de entorno."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or not api_key.strip():
        raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")
    return OpenAI(api_key=api_key.strip())


def build_prompt(evento_texto: str) -> list:
    """Construye el prompt para identificar eventos N1."""
    eventos_riesgo_n1 = [
        "Personas",
        "Fraude externo",
        "Fraude interno",
        "Seguridad física y seguridad laboral",
        "Continuidad del negocio",
        "Procesamiento y ejecución de transacciones",
        "Tecnología",
        "Conducta",
        "Legal",
        "Delito financiero",
        "Cumplimiento normativo",
        "Terceros",
        "Seguridad de la información (incluida ciberseguridad)",
        "Reporte legal y fiscal",
        "Gestión de datos",
        "Modelos"
    ]

    eventos_n1_str = "\n".join([f"- {e}" for e in eventos_riesgo_n1])

    prompt = f"""
Identifica qué Eventos de Riesgo Nivel 1 (N1) de ORX aplican al siguiente evento SARO.

Evento: "{evento_texto}"

Eventos de Riesgo N1 disponibles:
{eventos_n1_str}

Devuelve únicamente un array JSON con los nombres de los eventos que aplican:
["Evento 1", "Evento 2"]

Reglas:
- Usa exactamente los nombres de la lista.
- Incluye solo los eventos que aplican.
- Devuelve solo un array JSON, sin texto adicional.
"""
    return [
        {"role": "system", "content": "Eres un analista experto en riesgo operacional. Devuelve solo un array JSON con los eventos N1."},
        {"role": "user", "content": prompt}
    ]


def filter_riesgos_n2_por_contexto(evento_saro: str, n1: str, riesgos_n2: List[str], model: str = "gpt-4o-mini") -> List[str]:
    """Filtra los riesgos N2 que son relevantes según el contexto del evento SARO."""
    if not riesgos_n2:
        return []
    
    client = get_openai_client()
    
    riesgos_n2_str = "\n".join([f"- {r}" for r in riesgos_n2])
    
    prompt = f"""Dado el siguiente evento SARO y una lista de riesgos N2 del tipo "{n1}", 
identifica cuáles de estos riesgos N2 son realmente aplicables al evento.

Evento SARO:
"{evento_saro}"

Riesgo N1: {n1}

Riesgos N2 disponibles:
{riesgos_n2_str}

Devuelve únicamente un array JSON con los nombres exactos de los riesgos N2 que aplican al evento:
["Riesgo N2 1", "Riesgo N2 2"]

Reglas:
- Usa exactamente los nombres de la lista.
- Incluye solo los riesgos que son realmente relevantes para el evento descrito.
- Devuelve solo un array JSON, sin texto adicional."""

    messages = [
        {"role": "system", "content": "Eres un analista experto en riesgo operacional. Identificas riesgos N2 relevantes según el contexto del evento. Devuelve solo un array JSON."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )
    
    raw_output = response.choices[0].message.content.strip()
    
    # Extraer el array JSON
    match = re.search(r"\[.*\]", raw_output, re.DOTALL)
    if not match:
        return []
    
    json_text = match.group(0)
    try:
        result = json.loads(json_text)
        if isinstance(result, list):
            # Validar que los riesgos devueltos estén en la lista original
            return [r for r in result if r in riesgos_n2]
        return []
    except json.JSONDecodeError:
        return []


def extract_saro_json(evento_texto: str, evento_saro_original: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Extrae eventos N1 y riesgos N2 del evento SARO."""
    if not evento_texto or not evento_texto.strip():
        raise ValueError("La descripción del evento SARO no puede estar vacía.")

    client = get_openai_client()
    messages = build_prompt(evento_texto.strip())

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )

    raw_output = response.choices[0].message.content.strip()

    # Extraer el array JSON (entre corchetes)
    match = re.search(r"\[.*\]", raw_output, re.DOTALL)
    if not match:
        raise ValueError(f"No se encontró un array JSON válido en la respuesta: {raw_output}")

    json_text = match.group(0)
    try:
        result = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear JSON: {e}\nRespuesta: {json_text}")

    # Validar que sea lista
    if not isinstance(result, list):
        raise ValueError(f"La respuesta no es un array JSON: {result}")
    
    # Obtener todos los riesgos N2 posibles por N1
    riesgos_por_n1 = get_riesgos_n2_por_n1(result, RIESGOS_ORX_DATA)
    
    # Filtrar riesgos N2 según el contexto del evento SARO
    riesgos_filtrados = []
    for n1 in result:
        riesgos_n2_posibles = riesgos_por_n1.get(n1, [])
        if riesgos_n2_posibles:
            riesgos_n2_aplicables = filter_riesgos_n2_por_contexto(
                evento_saro_original, n1, riesgos_n2_posibles, model
            )
            if riesgos_n2_aplicables:
                riesgos_filtrados.append({
                    "Riesgo_nivel_1": n1,
                    "Riesgo_nivel_2": sorted(riesgos_n2_aplicables)
                })
    
    return {
        "eventos_n1": result,
        "riesgos": riesgos_filtrados
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de AWS Lambda.
    
    Espera recibir en el body del evento:
    - "descripcion": string con la descripción del evento SARO
    - "model": string opcional con el modelo de OpenAI (default: "gpt-4o-mini")
    
    Returns:
        Respuesta HTTP con el JSON de resultados
    """
    try:
        # Obtener el body del evento
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Obtener la descripción del evento SARO
        descripcion = body.get('descripcion') or body.get('descripcion_saro') or body.get('texto')
        
        if not descripcion or not descripcion.strip():
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'No se proporcionó la descripción del evento SARO',
                    'mensaje': 'El campo "descripcion" es requerido en el body de la petición'
                }, ensure_ascii=False)
            }
        
        # Obtener el modelo (opcional)
        model = body.get('model', 'gpt-4o-mini')
        
        # Procesar el evento SARO
        resultado = extract_saro_json(descripcion.strip(), descripcion.strip(), model)
        
        # Retornar respuesta exitosa
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(resultado, ensure_ascii=False)
        }
        
    except ValueError as e:
        # Error de validación
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Error de validación',
                'mensaje': str(e)
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        # Error interno del servidor
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'mensaje': str(e)
            }, ensure_ascii=False)
        }

