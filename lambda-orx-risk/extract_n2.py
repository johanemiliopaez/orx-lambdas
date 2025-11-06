from typing import Dict, List

# JSON de riesgos ORX incluido directamente en el código
RIESGOS_ORX_DATA = [
    {
        "Riesgo_nivel_1": "Gente",
        "Riesgo_nivel_2": "Incumplimiento de la legislación laboral o de los requisitos reglamentarios"
    },
    {
        "Riesgo_nivel_1": "Gente",
        "Riesgo_nivel_2": "Relaciones laborales ineficaces"
    },
    {
        "Riesgo_nivel_1": "Gente",
        "Riesgo_nivel_2": "Seguridad inadecuada en el lugar de trabajo"
    },
    {
        "Riesgo_nivel_1": "Fraude externo",
        "Riesgo_nivel_2": "Fraude de terceros/proveedores"
    },
    {
        "Riesgo_nivel_1": "Fraude externo",
        "Riesgo_nivel_2": "Fraude de agentes/corredores/intermediarios"
    },
    {
        "Riesgo_nivel_1": "Fraude externo",
        "Riesgo_nivel_2": "Fraude de primera parte"
    },
    {
        "Riesgo_nivel_1": "Fraude interno",
        "Riesgo_nivel_2": "Fraude interno cometido contra la organización"
    },
    {
        "Riesgo_nivel_1": "Fraude interno",
        "Riesgo_nivel_2": "Fraude interno cometido contra clientes o terceros"
    },
    {
        "Riesgo_nivel_1": "Seguridad física y protección",
        "Riesgo_nivel_2": "Daños a los activos físicos de la organización"
    },
    {
        "Riesgo_nivel_1": "Seguridad física y protección",
        "Riesgo_nivel_2": "Lesiones a empleados o afiliados fuera del lugar de trabajo"
    },
    {
        "Riesgo_nivel_1": "Seguridad física y protección",
        "Riesgo_nivel_2": "Daños o perjuicios al patrimonio público"
    },
    {
        "Riesgo_nivel_1": "Continuidad del negocio",
        "Riesgo_nivel_2": "Planificación de continuidad empresarial/gestión de eventos inadecuada"
    },
    {
        "Riesgo_nivel_1": "Procesamiento y ejecución de transacciones",
        "Riesgo_nivel_2": "Fallo de procesamiento/ejecución relacionado con clientes y productos"
    },
    {
        "Riesgo_nivel_1": "Procesamiento y ejecución de transacciones",
        "Riesgo_nivel_2": "Fallo de procesamiento/ejecución relacionado con valores y garantías"
    },
    {
        "Riesgo_nivel_1": "Procesamiento y ejecución de transacciones",
        "Riesgo_nivel_2": "Fallo de procesamiento/ejecución relacionado con terceros"
    },
    {
        "Riesgo_nivel_1": "Procesamiento y ejecución de transacciones",
        "Riesgo_nivel_2": "Fallo de procesamiento/ejecución relacionado con operaciones internas"
    },
    {
        "Riesgo_nivel_1": "Procesamiento y ejecución de transacciones",
        "Riesgo_nivel_2": "Error en la ejecución del cambio"
    },
    {
        "Riesgo_nivel_1": "Tecnología",
        "Riesgo_nivel_2": "Fallo de hardware"
    },
    {
        "Riesgo_nivel_1": "Tecnología",
        "Riesgo_nivel_2": "Fallo de software"
    },
    {
        "Riesgo_nivel_1": "Tecnología",
        "Riesgo_nivel_2": "Fallo de red"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Uso de información privilegiada"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Antimonopolio/anticompetencia"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Prácticas de mercado indebidas"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Falla del servicio de preventa"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Falla del servicio posventa"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Maltrato al cliente/incumplimiento de deberes hacia los clientes"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Mala gestión de cuentas de clientes"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Distribución/comercialización inadecuada"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Diseño inadecuado de producto/servicio"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Denuncia de irregularidades"
    },
    {
        "Riesgo_nivel_1": "Conducta",
        "Riesgo_nivel_2": "Incumplimiento del código de conducta y mala conducta de los empleados"
    },
    {
        "Riesgo_nivel_1": "Legal",
        "Riesgo_nivel_2": "Mal manejo de los procesos legales"
    },
    {
        "Riesgo_nivel_1": "Legal",
        "Riesgo_nivel_2": "Incumplimiento de derechos/obligaciones contractuales"
    },
    {
        "Riesgo_nivel_1": "Legal",
        "Riesgo_nivel_2": "Incumplimiento de derechos/obligaciones extracontractuales"
    },
    {
        "Riesgo_nivel_1": "Delitos financieros",
        "Riesgo_nivel_2": "Blanqueo de capitales y financiación del terrorismo"
    },
    {
        "Riesgo_nivel_1": "Delitos financieros",
        "Riesgo_nivel_2": "Violación de sanciones"
    },
    {
        "Riesgo_nivel_1": "Delitos financieros",
        "Riesgo_nivel_2": "Soborno y corrupción"
    },
    {
        "Riesgo_nivel_1": "Delitos financieros",
        "Riesgo_nivel_2": "Falla en el control de KYC y monitoreo de transacciones"
    },
    {
        "Riesgo_nivel_1": "Cumplimiento normativo",
        "Riesgo_nivel_2": "Relación ineficaz con los reguladores"
    },
    {
        "Riesgo_nivel_1": "Cumplimiento normativo",
        "Riesgo_nivel_2": "Respuesta inadecuada al cambio regulatorio"
    },
    {
        "Riesgo_nivel_1": "Cumplimiento normativo",
        "Riesgo_nivel_2": "Licencia/certificación/registro inadecuados"
    },
    {
        "Riesgo_nivel_1": "Cumplimiento normativo",
        "Riesgo_nivel_2": "Incumplimiento de actividades transfronterizas/regulaciones extraterritoriales"
    },
    {
        "Riesgo_nivel_1": "Cumplimiento normativo",
        "Riesgo_nivel_2": "Riesgo prudencial"
    },
    {
        "Riesgo_nivel_1": "Tercero",
        "Riesgo_nivel_2": "Fallo en el control de gestión de terceros"
    },
    {
        "Riesgo_nivel_1": "Tercero",
        "Riesgo_nivel_2": "Fallo en la selección de terceros"
    },
    {
        "Riesgo_nivel_1": "Tercero",
        "Riesgo_nivel_2": "Supervisión continua deficiente de terceros"
    }
]

# Mapeo de nombres N1 del extract_saro.py a los nombres en el JSON
N1_NAME_MAPPING = {
    "Personas": "Gente",
    "Terceros": "Tercero",
    "Seguridad física y seguridad laboral": "Seguridad física y protección",
    "Delito financiero": "Delitos financieros",
    # Los demás deberían coincidir exactamente
}


def normalize_n1_name(n1_name: str) -> str:
    """
    Normaliza el nombre N1 para que coincida con el formato del JSON.
    """
    return N1_NAME_MAPPING.get(n1_name, n1_name)


def extract_n2_riesgos(n1_list: List[str], riesgos_data: List[Dict[str, str]]) -> List[str]:
    """
    Extrae los riesgos N2 correspondientes a los N1 proporcionados.
    
    Args:
        n1_list: Lista de nombres de riesgos N1
        riesgos_data: Datos del JSON de riesgos ORX
    
    Returns:
        Lista única de riesgos N2 ordenada
    """
    n2_riesgos = []
    n1_normalized = [normalize_n1_name(n1) for n1 in n1_list]
    
    # Buscar todos los riesgos N2 que correspondan a los N1 proporcionados
    for riesgo in riesgos_data:
        riesgo_n1 = riesgo.get("Riesgo_nivel_1", "")
        riesgo_n2 = riesgo.get("Riesgo_nivel_2", "")
        
        if riesgo_n1 in n1_normalized and riesgo_n2:
            if riesgo_n2 not in n2_riesgos:
                n2_riesgos.append(riesgo_n2)
    
    return sorted(n2_riesgos)

