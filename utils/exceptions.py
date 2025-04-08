# utils/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

def custom_error_404(request, exception=None):
    """
    Maneja errores 404 (Recurso no encontrado).
    """
    response = {
        "status": "error",
        "message": "Recurso no encontrado",
        "data": None,
        "code": 404,
        "errors": None,
    }
    return JsonResponse(response, status=404)

def custom_error_500(request):
    """
    Maneja errores 500 (Error interno del servidor).
    """
    response = {
        "status": "error",
        "message": "Error interno del servidor",
        "data": None,
        "code": 500,
        "errors": None,
    }
    return JsonResponse(response, status=500)

def custom_exception_handler(exc, context):
    """
    Maneja excepciones de DRF y devuelve respuestas estructuradas.
    """
    # Llama al manejador de excepciones por defecto para obtener la respuesta estándar
    response = exception_handler(exc, context)

    if response is not None:
        # Personaliza la respuesta de error
        response.data = {
            "status": "error",
            "message": response.data.get("detail", "Error desconocido"),
            "data": None,
            "code": response.status_code,
            "errors": response.data,
        }
    else:
        # Maneja excepciones no capturadas (por ejemplo, errores 500)
        response = Response(
            {
                "status": "error",
                "message": "Error interno del servidor",
                "data": None,
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "errors": [],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response