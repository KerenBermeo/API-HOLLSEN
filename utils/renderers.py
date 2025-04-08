from rest_framework.renderers import JSONRenderer
from rest_framework import status

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None

        # Determinar si la respuesta es de éxito o error
        status_type = "error" if response and response.status_code >= 400 else "success"

        # Manejar datos según el tipo de respuesta
        if isinstance(data, dict):
            # Caso de paginación: se detecta si existen las claves "results", "count", etc.
            if "results" in data and "count" in data:
                structured_data = {
                    "count": data["count"],
                    "next": data["next"],
                    "previous": data["previous"],
                    "items": data["results"]  # Guardar los resultados en "items"
                }
            else:
                structured_data = data.get("data", data)  # Si no es paginación, usa "data" normalmente

            message = data.get("message", "Operación exitosa." if status_type == "success" else "Ocurrió un error.")
            errors = data.get("errors", [])

        elif isinstance(data, list):
            # Si `data` es una lista (sin paginación), simplemente la usamos como "data"
            structured_data = data
            message = "Operación exitosa." if status_type == "success" else "Ocurrió un error."
            errors = []

        elif data is None:
            message = "No hay datos disponibles."
            structured_data = {}
            errors = []

        else:
            message = str(data)
            structured_data = str(data)
            errors = []

        # Construir la respuesta final con la estructura esperada
        structured_response = {
            "status": status_type,
            "message": message,
            "data": structured_data,  # Ahora soporta listas y paginación
            "code": response.status_code if response else status.HTTP_200_OK,
            "errors": errors
        }

        return super().render(structured_response, accepted_media_type, renderer_context)
