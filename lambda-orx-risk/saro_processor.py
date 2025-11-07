import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI
from extract_n2 import RIESGOS_ORX_DATA, normalize_n1_name

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def get_riesgos_n2_por_n1(n1_list: List[str], riesgos_data: List[Dict[str, str]]) -> Dict[str, List[str]]:
    riesgos_por_n1 = {}
    n1_normalized = {normalize_n1_name(n1): n1 for n1 in n1_list}
    
    for riesgo in riesgos_data:
        riesgo_n1_json = riesgo.get("Riesgo_nivel_1", "")
        riesgo_n2 = riesgo.get("Riesgo_nivel_2", "")
        
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


def filter_riesgos_n2_por_contexto(evento_saro: str, n1: str, riesgos_n2: List[str], model: str = "gpt-4o-mini") -> List[str]:
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
"""
    messages = [
        {"role": "system", "content": "Eres un analista experto en riesgo operacional. Devuelve solo un array JSON."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )
    
    raw_output = response.choices[0].message.content.strip()
    match = re.search(r"\[.*\]", raw_output, re.DOTALL)
    if not match:
        return []
    
    try:
        result = json.loads(match.group(0))
        return [r for r in result if r in riesgos_n2] if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []


def get_openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY no está configurada")
    return OpenAI(api_key=OPENAI_API_KEY)


def build_prompt(evento_texto: str) -> list:
    eventos_riesgo_n1 = [
        "Personas", "Fraude externo", "Fraude interno",
        "Seguridad física y seguridad laboral", "Continuidad del negocio",
        "Procesamiento y ejecución de transacciones", "Tecnología",
        "Conducta", "Legal", "Delito financiero", "Cumplimiento normativo",
        "Terceros", "Seguridad de la información (incluida ciberseguridad)",
        "Reporte legal y fiscal", "Gestión de datos", "Modelos"
    ]
    eventos_n1_str = "\n".join([f"- {e}" for e in eventos_riesgo_n1])

    prompt = f"""
Identifica qué Eventos de Riesgo Nivel 1 (N1) de ORX aplican al siguiente evento SARO.

Evento: "{evento_texto}"

Eventos de Riesgo N1 disponibles:
{eventos_n1_str}

Devuelve únicamente un array JSON con los nombres de los eventos que aplican:
["Evento 1", "Evento 2"]
"""
    return [
        {"role": "system", "content": "Eres un analista experto en riesgo operacional. Devuelve solo un array JSON."},
        {"role": "user", "content": prompt}
    ]


def extract_saro_json(evento_texto: str, evento_saro_original: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    if not evento_texto.strip():
        raise ValueError("La descripción del evento SARO no puede estar vacía.")

    client = get_openai_client()
    messages = build_prompt(evento_texto.strip())

    response = client.chat.completions.create(model=model, messages=messages, temperature=0.0)
    raw_output = response.choices[0].message.content.strip()

    match = re.search(r"\[.*\]", raw_output, re.DOTALL)
    if not match:
        raise ValueError(f"No se encontró un array JSON válido en la respuesta: {raw_output}")

    try:
        result = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear JSON: {e}\nRespuesta: {raw_output}")

    riesgos_por_n1 = get_riesgos_n2_por_n1(result, RIESGOS_ORX_DATA)
    
    riesgos_filtrados = []
    for n1 in result:
        riesgos_n2_posibles = riesgos_por_n1.get(n1, [])
        if riesgos_n2_posibles:
            riesgos_n2_aplicables = filter_riesgos_n2_por_contexto(evento_saro_original, n1, riesgos_n2_posibles, model)
            if riesgos_n2_aplicables:
                riesgos_filtrados.append({
                    "Riesgo_nivel_1": n1,
                    "Riesgo_nivel_2": sorted(riesgos_n2_aplicables)
                })
    
    return {"eventos_n1": result, "riesgos": riesgos_filtrados}
