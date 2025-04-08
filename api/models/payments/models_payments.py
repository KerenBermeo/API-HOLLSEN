from django.db import models
from api.models.orders.models_orders import Order

class OrderPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=30)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    gateway_response = models.JSONField(blank=True, null=True, help_text="Respuesta cruda del pasarela")

    class Meta:
        db_table = 'order_payments'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Pago de {self.amount} para {self.order.order_number}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Creado'),
        ('approved', 'Aprobado'),
        ('pending', 'Pendiente'),
        ('rejected', 'Rechazado'),
        ('refunded', 'Reembolsado'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='paypal_payments')
    paypal_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['paypal_id']),
        ]

    def __str__(self):
        return f"Pago PayPal {self.paypal_id} - {self.status}"