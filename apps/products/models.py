from django.db import models
from django.contrib.postgres.fields import ArrayField

class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=50, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')

    class Meta:
        db_table = 'product_categories'
        verbose_name_plural = 'product categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_customizable = models.BooleanField(default=False, help_text="Si acepta personalización")
    base_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Precio base sin personalización")
    color_options = ArrayField(models.CharField(max_length=50), blank=True, null=True, help_text="Colores disponibles: JSON array")
    categories = models.ManyToManyField(ProductCategory, through='ProductCategoryAssignment')

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    price_override = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_variants'

    def __str__(self):
        return f"{self.product.name} - {self.description}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url = models.URLField()
    alt_text = models.CharField(max_length=100, blank=True, null=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        db_table = 'product_images'

    def __str__(self):
        return f"Imagen de {self.product.name}"

class ProductCategoryAssignment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_category_assignments'
        unique_together = ('product', 'category')

    def __str__(self):
        return f"{self.product.name} en {self.category.name}"

class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Estrella'),
        (2, '2 Estrellas'),
        (3, '3 Estrellas'),
        (4, '4 Estrellas'),
        (5, '5 Estrellas'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_reviews'

    def __str__(self):
        return f"Reseña de {self.user.email} para {self.product.name}"
