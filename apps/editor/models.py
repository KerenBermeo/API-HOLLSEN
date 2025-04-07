from django.db import models
from users.models import User
from products.models import Product

class CustomDesign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designs')
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_designs')
    design_image_url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    colors = models.CharField(max_length=100, blank=True, null=True, help_text="Colores usados en el diseño")
    design_parameters = models.JSONField(help_text="Configuración del editor")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'custom_designs'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['base_product']),
        ]

    def __str__(self):
        return f"Diseño personalizado de {self.user.email} para {self.base_product.name}"