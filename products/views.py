from django.shortcuts import render
from .parser import ProductCitilink
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Catalog, Category, Product


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def index(request):
    parsers_product_without_citilink = ProductCitilink()
    parsers_product_without_citilink.parser_citilink()
    for catalog, category_list in parsers_product_without_citilink.CATALOG_AND_CATEGORY.items():
        catalog_models = Catalog()
        catalog_models.name_catalog = catalog
        catalog_models.save()
        for category in category_list:
            category_models = Category()
            category_models.catalog = Catalog.objects.get(name_catalog=catalog)
            category_models.name_category = category
            category_models.save()
    for product_name, product_info in parsers_product_without_citilink.PRODUCT.items():
        category_models = Category.objects.get(name_category="Смартфоны")
        product = Product()
        product.category = category_models
        product.name_product = product_info['name']
        product.photo_product = product_info['url_img']
        product.price_product = product_info['price']
        product.save()
    return Response("Данные о товарах было успешно загружены в базу")