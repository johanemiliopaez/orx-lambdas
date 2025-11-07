from typing import Dict, List

RIESGOS_ORX_DATA = [
    {"Riesgo_nivel_1": "Gente", "Riesgo_nivel_2": "Incumplimiento de la legislación laboral o de los requisitos reglamentarios"},
    {"Riesgo_nivel_1": "Gente", "Riesgo_nivel_2": "Relaciones laborales ineficaces"},
    {"Riesgo_nivel_1": "Gente", "Riesgo_nivel_2": "Seguridad inadecuada en el lugar de trabajo"},
    {"Riesgo_nivel_1": "Fraude externo", "Riesgo_nivel_2": "Fraude de terceros/proveedores"},
    {"Riesgo_nivel_1": "Fraude externo", "Riesgo_nivel_2": "Fraude de agentes/corredores/intermediarios"},
    {"Riesgo_nivel_1": "Fraude externo", "Riesgo_nivel_2": "Fraude de primera parte"},
    {"Riesgo_nivel_1": "Fraude interno", "Riesgo_nivel_2": "Fraude interno cometido contra la organización"},
    {"Riesgo_nivel_1": "Fraude interno", "Riesgo_nivel_2": "Fraude interno cometido contra clientes o terceros"},
    {"Riesgo_nivel_1": "Seguridad física y protección", "Riesgo_nivel_2": "Daños a los activos físicos de la organización"},
    {"Riesgo_nivel_1": "Continuidad del negocio", "Riesgo_nivel_2": "Planificación de continuidad empresarial/gestión de eventos inadecuada"},
    {"Riesgo_nivel_1": "Procesamiento y ejecución de transacciones", "Riesgo_nivel_2": "Fallo de procesamiento/ejecución relacionado con clientes y productos"},
    {"Riesgo_nivel_1": "Procesamiento y ejecución de transacciones", "Riesgo_nivel_2": "Fallo de procesamiento/ejecución relacionado con operaciones internas"},
    {"Riesgo_nivel_1": "Tecnología", "Riesgo_nivel_2": "Fallo de software"},
    {"Riesgo_nivel_1": "Tecnología", "Riesgo_nivel_2": "Fallo de red"},
    {"Riesgo_nivel_1": "Tecnología", "Riesgo_nivel_2": "Fallo de hardware"},
]

N1_NAME_MAPPING = {
    "Personas": "Gente",
    "Terceros": "Tercero",
    "Seguridad física y seguridad laboral": "Seguridad física y protección",
    "Delito financiero": "Delitos financieros"
}

def normalize_n1_name(n1_name: str) -> str:
    return N1_NAME_MAPPING.get(n1_name, n1_name)
