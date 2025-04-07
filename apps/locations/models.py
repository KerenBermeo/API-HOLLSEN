from django.contrib.gis.db import models as gis_models
from django.db import models

class Departamento(models.Model):
    codigo_dane = models.CharField(max_length=2, primary_key=True)
    nombre = models.CharField(max_length=50)
    indicativo_telefonico = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        db_table = 'departamentos'
        ordering = ['nombre']
        verbose_name = 'departamento'
        verbose_name_plural = 'departamentos'

    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    TIPO_CHOICES = [
        ('MUNICIPIO', 'Municipio'),
        ('DISTRITO', 'Distrito'),
        ('CORREGIMIENTO', 'Corregimiento'),
    ]
    
    CATEGORIA_CHOICES = [
        ('A', 'Categoría A'),
        ('B', 'Categoría B'),
        ('C', 'Categoría C'),
    ]
    
    codigo_dane = models.CharField(max_length=5, primary_key=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=60)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='MUNICIPIO')
    categoria = models.CharField(max_length=1, choices=CATEGORIA_CHOICES, blank=True, null=True)
    icao_code = models.CharField(max_length=4, blank=True, null=True)
    rios_importantes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'municipios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Barrio(models.Model):
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=70)
    codigo_dane = models.CharField(max_length=10, blank=True, null=True)
    comuna = models.CharField(max_length=2, blank=True, null=True, help_text="División administrativa Cali")
    area_hectareas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    perimetro_metros = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    limite_geografico = gis_models.PolygonField(blank=True, null=True, help_text="Geometría del barrio")

    class Meta:
        db_table = 'barrios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre}, {self.municipio.nombre}"

class Address(models.Model):
    TIPO_VIA_CHOICES = [
        ('AV', 'Avenida'),
        ('CL', 'Calle'),
        ('KR', 'Carrera'),
        ('DG', 'Diagonal'),
        ('TV', 'Transversal'),
    ]
    
    SECTOR_CHOICES = [
        ('NORTE', 'Norte'),
        ('SUR', 'Sur'),
        ('ESTE', 'Este'),
        ('OESTE', 'Oeste'),
    ]
    
    COMPLEMENTO_TIPO_CHOICES = [
        ('AP', 'Apartamento'),
        ('BLQ', 'Bloque'),
        ('ED', 'Edificio'),
        ('LT', 'Lote'),
        ('MN', 'Manzana'),
        ('OF', 'Oficina'),
        ('PN', 'Piso'),
        ('UR', 'Urbanización'),
    ]
    
    VERIFICACION_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
        ('INVALIDO', 'Inválido'),
    ]
    
    FUENTE_CHOICES = [
        ('DAPM', 'Departamento Administrativo de Planeación Municipal'),
        ('GOOGLE', 'Google Maps'),
        ('MANUAL', 'Ingreso Manual'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='addresses')
    
    # Estructura jerárquica
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT)
    barrio = models.ForeignKey(Barrio, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Vía principal
    tipo_via_principal = models.CharField(max_length=3, choices=TIPO_VIA_CHOICES)
    numero_via_principal = models.CharField(max_length=10)
    letra_via_principal = models.CharField(max_length=1, blank=True, null=True)
    bis_principal = models.CharField(max_length=3, blank=True, null=True)
    sector_geografico_principal = models.CharField(max_length=5, choices=SECTOR_CHOICES, blank=True, null=True)
    
    # Vía generadora (cruce)
    tipo_via_generadora = models.CharField(max_length=3, choices=TIPO_VIA_CHOICES, blank=True, null=True)
    numero_via_generadora = models.CharField(max_length=10, blank=True, null=True)
    letra_via_generadora = models.CharField(max_length=1, blank=True, null=True)
    bis_generadora = models.CharField(max_length=3, blank=True, null=True)
    sector_geografico_generadora = models.CharField(max_length=5, choices=SECTOR_CHOICES, blank=True, null=True)
    
    # Placa domiciliaria
    numero_placa = models.CharField(max_length=10)
    
    # Complementos (hasta 4 niveles)
    complemento_1_tipo = models.CharField(max_length=5, choices=COMPLEMENTO_TIPO_CHOICES, blank=True, null=True)
    complemento_1_valor = models.CharField(max_length=10, blank=True, null=True)
    complemento_2_tipo = models.CharField(max_length=5, choices=COMPLEMENTO_TIPO_CHOICES, blank=True, null=True)
    complemento_2_valor = models.CharField(max_length=10, blank=True, null=True)
    complemento_3_tipo = models.CharField(max_length=5, choices=COMPLEMENTO_TIPO_CHOICES, blank=True, null=True)
    complemento_3_valor = models.CharField(max_length=10, blank=True, null=True)
    complemento_4_tipo = models.CharField(max_length=5, choices=COMPLEMENTO_TIPO_CHOICES, blank=True, null=True)
    complemento_4_valor = models.CharField(max_length=10, blank=True, null=True)
    
    # Códigos oficiales
    codigo_postal = models.CharField(max_length=6, blank=True, null=True)
    estrato = models.IntegerField(blank=True, null=True, help_text="1-6 para análisis")
    upz = models.CharField(max_length=5, blank=True, null=True, help_text="Unidad de Planeamiento Zonal")
    
    # Validación
    verificacion_estado = models.CharField(max_length=20, choices=VERIFICACION_CHOICES, default='PENDIENTE')
    geolocalizacion = gis_models.PointField(blank=True, null=True, help_text="Coordenadas EPSG:4686 (MAGNA-SIRGAS)")
    fuente_geolocalizacion = models.CharField(max_length=20, choices=FUENTE_CHOICES, blank=True, null=True)
    
    # Metadata
    es_principal = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'addresses'
        verbose_name = 'dirección'
        verbose_name_plural = 'direcciones'
        indexes = [
            models.Index(fields=['user', 'es_principal']),
            models.Index(fields=['municipio', 'barrio']),
            models.Index(fields=['codigo_postal']),
        ]

    def __str__(self):
        return f"Dirección en {self.municipio.nombre} ({self.user.email})"