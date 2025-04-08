from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from ..locations.models_locations import Address
from ..products.models_products import Product, ProductVariant
from api.models.editor.models_editor import CustomDesign
from django.conf import settings


User = settings.AUTH_USER_MODEL 

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PAID = 'paid', 'Pagado'
        PROCESSING = 'processing', 'Procesando'
        SHIPPED = 'shipped', 'Enviado'
        DELIVERED = 'delivered', 'Entregado'
        CANCELLED = 'cancelled', 'Cancelado'
        REFUNDED = 'refunded', 'Reembolsado'

    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'credit_card', 'Tarjeta de crédito'
        PAYPAL = 'paypal', 'PayPal'
        BANK_TRANSFER = 'bank_transfer', 'Transferencia bancaria'
        CASH = 'cash', 'Efectivo'
        NEQUI = 'nequi', 'Nequi'
        DAVIPLATA = 'daviplata', 'Daviplata'

    class ShippingMethod(models.TextChoices):
        STANDARD = 'standard', 'Estándar'
        EXPRESS = 'express', 'Express'
        PICKUP = 'pickup', 'Recoger en tienda'

    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Usuario'
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name='shipping_orders',
        verbose_name='Dirección de envío'
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name='billing_orders',
        verbose_name='Dirección de facturación'
    )

    # Información de la orden
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de orden'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )

    # Fechas importantes
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )
    paid_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de pago'
    )
    cancelled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de cancelación'
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de entrega'
    )

    # Totales financieros
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal'
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Impuestos'
    )
    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Costo de envío'
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Descuento'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Total'
    )

    # Métodos
    payment_method = models.CharField(
        max_length=30,
        choices=PaymentMethod.choices,
        blank=True,
        null=True,
        verbose_name='Método de pago'
    )
    shipping_method = models.CharField(
        max_length=30,
        choices=ShippingMethod.choices,
        blank=True,
        null=True,
        verbose_name='Método de envío'
    )

    # Metadata
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Dirección IP'
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='Agente de usuario'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    internal_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas internas'
    )

    class Meta:
        db_table = 'orders'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user'], name='idx_order_user'),
            models.Index(fields=['order_number'], name='idx_order_number'),
            models.Index(fields=['status'], name='idx_order_status'),
            models.Index(fields=['created_at'], name='idx_order_created_at'),
            models.Index(fields=['payment_method'], name='idx_order_payment_method'),
        ]

    def __str__(self):
        return f"Orden #{self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        # Actualizar automáticamente la fecha de actualización
        self.updated_at = timezone.now()
        
        # Si el estado cambia a pagado, registrar la fecha
        if self.status == self.Status.PAID and not self.paid_at:
            self.paid_at = timezone.now()
        
        # Si el estado cambia a cancelado, registrar la fecha
        if self.status == self.Status.CANCELLED and not self.cancelled_at:
            self.cancelled_at = timezone.now()
        
        # Si el estado cambia a entregado, registrar la fecha
        if self.status == self.Status.DELIVERED and not self.delivered_at:
            self.delivered_at = timezone.now()
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    # Relaciones principales
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Producto'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Variante'
    )
    custom_design = models.ForeignKey(
        CustomDesign,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Diseño personalizado'
    )

    # Datos snapshot al momento de la compra
    product_name = models.CharField(
        max_length=100,
        verbose_name='Nombre del producto'
    )
    variant_description = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Descripción de la variante'
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Cantidad'
    )
    design_preview_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL de vista previa del diseño'
    )

    # Relación con producto original (si fue reemplazado)
    original_product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='replaced_in_orders',
        verbose_name='Producto original'
    )

    # Total calculado
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Subtotal'
    )

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Ítem de pedido'
        verbose_name_plural = 'Ítems de pedido'
        indexes = [
            models.Index(fields=['order'], name='idx_order_item_order'),
            models.Index(fields=['product'], name='idx_order_item_product'),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product_name} en orden #{self.order.order_number}"

    def save(self, *args, **kwargs):
        # Calcular automáticamente el subtotal si no está definido
        if not self.subtotal:
            self.subtotal = self.unit_price * self.quantity
        
        # Snapshot del nombre del producto si no está definido
        if not self.product_name and self.product:
            self.product_name = self.product.name
        
        # Snapshot de la descripción de la variante si no está definido
        if not self.variant_description and self.variant:
            self.variant_description = self.variant.description
        
        super().save(*args, **kwargs)

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Pedido'
    )
    old_status = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Estado anterior'
    )
    new_status = models.CharField(
        max_length=20,
        verbose_name='Nuevo estado'
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de cambio'
    )
    changed_by = models.CharField(
        max_length=50,
        verbose_name='Cambiado por'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )

    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Historial de estado de pedido'
        verbose_name_plural = 'Historiales de estados de pedidos'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['order'], name='idx_status_history_order'),
            models.Index(fields=['changed_at'], name='idx_status_history_changed_at'),
        ]

    def __str__(self):
        return f"Cambio de estado de {self.old_status} a {self.new_status} para orden #{self.order.order_number}"

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='carts',
        verbose_name='Usuario'
    )
    session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID de sesión'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )

    class Meta:
        db_table = 'shopping_carts'
        verbose_name = 'Carrito de compras'
        verbose_name_plural = 'Carritos de compras'
        indexes = [
            models.Index(fields=['user'], name='idx_cart_user'),
            models.Index(fields=['session_id'], name='idx_cart_session'),
        ]

    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.email}"
        return f"Carrito de sesión {self.session_id}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrito'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Producto'
    )
    custom_design = models.ForeignKey(
        CustomDesign,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Diseño personalizado'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de agregado'
    )

    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Ítem de carrito'
        verbose_name_plural = 'Ítems de carrito'
        constraints = [
            models.CheckConstraint(
                check=models.Q(product__isnull=False) | models.Q(custom_design__isnull=False),
                name='product_or_design_required'
            )
        ]
        indexes = [
            models.Index(fields=['cart'], name='idx_cart_item_cart'),
        ]

    def __str__(self):
        if self.product:
            return f"{self.quantity}x {self.product.name} en carrito"
        return f"{self.quantity}x diseño personalizado en carrito"

    def save(self, *args, **kwargs):
        # Establecer el precio basado en el producto o diseño personalizado
        if not self.price:
            if self.product:
                self.price = self.product.price
            elif self.custom_design and self.custom_design.base_product:
                self.price = self.custom_design.base_product.price
        
        super().save(*args, **kwargs)