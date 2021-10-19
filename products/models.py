from django.db import models


class Catalog(models.Model):
    name_catalog = models.CharField(max_length=255, verbose_name="Название каталога", null=True, blank=True)

    class Meta:
        verbose_name = "Каталог"
        verbose_name_plural = "Каталоги"

    def __str__(self):
        return self.name_catalog


class Category(models.Model):
    catalog = models.ForeignKey(Catalog, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Каталог")
    name_category = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название каталога")

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return f'{self.name_category} из каталога {self.catalog.name_catalog}'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name="Категория товара")
    name_product = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название продукта")
    photo_product = models.ImageField(upload_to="media/product/", blank=True, null=True, verbose_name="Фото товара")
    price_product = models.CharField(max_length=255, null=True, blank=True, verbose_name="Цена товара")

    class Meta:
        verbose_name = "Информация продукта"
        verbose_name_plural = "Информация о продуктах"

    def __str__(self):
        return self.name_product
