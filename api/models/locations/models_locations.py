from django.db import models

class Departamento(models.Model):
    codigo_dane = models.CharField(max_length=2, primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    indicativo_telefonico = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'departamentos'

    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    TIPO_MUNICIPIO = 'MUNICIPIO'
    TIPO_DISTRITO = 'DISTRITO'
    TIPO_CHOICES = [
        (TIPO_MUNICIPIO, 'Municipio'),
        (TIPO_DISTRITO, 'Distrito'),
    ]
    
    CATEGORIA_CHOICES = [
        ('A', 'Categoría A'),
        ('B', 'Categoría B'),
        ('C', 'Categoría C'),
    ]
    
    codigo_dane = models.CharField(max_length=5, primary_key=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='municipios')
    nombre = models.CharField(max_length=60)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default=TIPO_MUNICIPIO)
    categoria = models.CharField(max_length=1, choices=CATEGORIA_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ['nombre']
        unique_together = ('departamento', 'nombre')

    def __str__(self):
        return f"{self.nombre}, {self.departamento}"

class Barrio(models.Model):
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, related_name='barrios')
    nombre = models.CharField(max_length=70)
    comuna = models.CharField(max_length=2, blank=True, null=True)
    estrato_promedio = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['nombre']
        unique_together = ('municipio', 'nombre')

    def __str__(self):
        return f"{self.nombre}, {self.municipio}"

class Direccion(models.Model):
    TIPO_VIA_CHOICES = [
        ('AV', 'Avenida'),
        ('CL', 'Calle'),
        ('KR', 'Carrera'),
        ('DG', 'Diagonal'),
    ]
    
    COMPLEMENTO_CHOICES = [
        ('AP', 'Apartamento'),
        ('BLQ', 'Bloque'),
        ('ED', 'Edificio'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='direcciones')
    barrio = models.ForeignKey(Barrio, on_delete=models.PROTECT)
    
    # Dirección básica
    tipo_via = models.CharField(max_length=3, choices=TIPO_VIA_CHOICES)
    numero_via = models.CharField(max_length=10)
    complemento_tipo = models.CharField(max_length=3, choices=COMPLEMENTO_CHOICES, blank=True, null=True)
    complemento_valor = models.CharField(max_length=10, blank=True, null=True)
    
    # Georeferenciación simple
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Metadata
    es_principal = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'direcciones'
        indexes = [
            models.Index(fields=['user', 'es_principal']),
            models.Index(fields=['barrio']),
        ]

    def direccion_completa(self):
        parts = [
            f"{self.get_tipo_via_display()} {self.numero_via}",
            f"{self.get_complemento_tipo_display()} {self.complemento_valor}" if self.complemento_tipo else None,
            str(self.barrio)
        ]
        return ", ".join(filter(None, parts))

    def __str__(self):
        return self.direccion_completa()

from django.db import models

class Address(models.Model):
    # Choices simplificados pero manteniendo los esenciales
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
    
    COMPLEMENTO_CHOICES = [
        ('AP', 'Apartamento'),
        ('BLQ', 'Bloque'),
        ('ED', 'Edificio'),
        ('PN', 'Piso'),
        ('UR', 'Urbanización'),
    ]
    
    ESTADO_VERIFICACION = [
        ('PENDIENTE', 'Pendiente'),
        ('VERIFICADO', 'Verificado'),
        ('INVALIDO', 'Inválido'),
    ]
    
    FUENTE_GEOLOCALIZACION = [
        ('DAPM', 'Datos Oficiales'),
        ('GOOGLE', 'Google Maps'),
        ('MANUAL', 'Manual'),
    ]

    # Relaciones (jerarquía geográfica)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='direcciones')
    municipio = models.ForeignKey('Municipio', on_delete=models.PROTECT)
    barrio = models.ForeignKey('Barrio', on_delete=models.SET_NULL, blank=True, null=True)

    # Dirección principal (estructura simplificada pero completa)
    tipo_via = models.CharField('Tipo de vía', max_length=3, choices=TIPO_VIA_CHOICES)
    numero_via = models.CharField('Número', max_length=10)
    letra_via = models.CharField('Letra', max_length=1, blank=True, null=True)
    bis = models.BooleanField('Tiene bis?', default=False)
    sector = models.CharField('Sector', max_length=5, choices=SECTOR_CHOICES, blank=True, null=True)
    
    # Complemento de dirección (estructura flexible)
    complemento = models.JSONField('Complementos', blank=True, null=True, help_text="Estructura: [{'tipo': 'AP', 'valor': '101'}, ...]")
    
    # Datos de localización
    codigo_postal = models.CharField('Código Postal', max_length=6, blank=True, null=True)
    estrato = models.PositiveSmallIntegerField('Estrato', blank=True, null=True, choices=[(i, str(i)) for i in range(1, 7)])
    
    # Geolocalización (sin GDAL)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    precision_geoloc = models.CharField('Precisión', max_length=10, blank=True, null=True)
    fuente_geoloc = models.CharField('Fuente', max_length=20, choices=FUENTE_GEOLOCALIZACION, blank=True, null=True)
    
    # Estado y metadatos
    verificada = models.BooleanField('Verificada', default=False)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_VERIFICACION, default='PENDIENTE')
    es_principal = models.BooleanField('Principal', default=False)
    creado = models.DateTimeField('Creado', auto_now_add=True)
    actualizado = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        indexes = [
            models.Index(fields=['user', 'es_principal']),
            models.Index(fields=['municipio', 'barrio']),
            models.Index(fields=['codigo_postal']),
        ]
        ordering = ['-es_principal', 'municipio__nombre', 'barrio__nombre']

    def direccion_completa(self):
        """Genera la dirección completa en formato estándar"""
        parts = [
            f"{self.get_tipo_via_display()} {self.numero_via}{self.letra_via or ''}",
            "BIS" if self.bis else None,
            f"{self.get_sector_display()}" if self.sector else None,
            f"Barrio {self.barrio.nombre}" if self.barrio else None,
            f"{self.municipio.nombre}, {self.municipio.departamento.nombre}"
        ]
        return " ".join(filter(None, parts))

    def __str__(self):
        return f"Dirección de {self.user} en {self.municipio}"

    def save(self, *args, **kwargs):
        """Lógica adicional al guardar"""
        # Auto-verificar si tiene coordenadas de fuente confiable
        if self.latitud and self.longitud and self.fuente_geoloc in ['DAPM', 'GOOGLE']:
            self.verificada = True
            self.estado = 'VERIFICADO'
        super().save(*args, **kwargs)