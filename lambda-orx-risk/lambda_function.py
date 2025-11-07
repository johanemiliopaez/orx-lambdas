import json
import saro_processor as sp

def lambda_handler(event, context):
    """
    Entrada esperada:
    {
      "descripcion": "La tesorería del banco no pudo operar durante 3 horas..."
    }
    """
    try:
        descripcion = event.get("descripcion", "").strip()
        if not descripcion:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Falta el campo 'descripcion'"}, ensure_ascii=False)
            }

        resultado = sp.extract_saro_json(descripcion, descripcion)

        return {
            "statusCode": 200,
            "body": json.dumps(resultado, ensure_ascii=False)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }
