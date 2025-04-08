from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # Tamaño de página por defecto
    page_size_query_param = 'page_size'  # Parámetro para cambiar el tamaño de página
    max_page_size = 100  # Tamaño máximo de página permitido

    def get_paginated_response(self, data):
        """
        Devuelve una respuesta paginada estandarizada.
        """
        response_data = {
            "status": "success",
            "message": "Datos obtenidos correctamente.",
            "data": {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
            "code": status.HTTP_200_OK,
            "errors": [],
        }
        return Response(response_data)