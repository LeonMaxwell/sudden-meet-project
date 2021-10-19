import requests
from bs4 import BeautifulSoup
import re


class ProductCitilink:
    """ Класс парсинга товаров с сайта Citilink. В результате получаем словарь который хранит каталог, категорию
    товаров, а так же информация о товарах. """

    CATALOG_LIST = list()
    CATEGORY_LIST = list()
    CATALOG_AND_CATEGORY = dict()
    CATEGORY_HREF = list()
    PRODUCT = dict()

    def parser_catalog_and_category_product(self, bs):
        # Парсинг каталогов и категорий товаров с их ссылками
        objects = bs.find_all('li', class_='CatalogLayout__item-list')
        for obj in objects:
            name_catolog = obj.find('span', class_='CatalogLayout__category-title')
            for catalog in name_catolog:
                self.CATALOG_LIST.append(re.sub("^\s+|\n|\r|\s+$", '', catalog))
                childer_category = obj.find('ul', class_='CatalogLayout__children-list')
                for child in childer_category:
                    name_category = child.find('a', class_='Link')
                    for category in name_category:
                        self.CATEGORY_LIST.append(category)
                        self.CATEGORY_HREF.append(name_category.attrs["href"])
                self.CATALOG_AND_CATEGORY.update({re.sub("^\s+|\n|\r|\s+$", '', catalog): self.CATEGORY_LIST.copy()})
                self.CATEGORY_LIST.clear()

    def parser_catalog_menu(self, bs, index, headers):
        # функция которая парсит специальные подкатегории товаров
        first_change = False
        list_href_menu_item = list()
        item_catalog_menu = bs.find_all('div', class_='CatalogCategoryMenu__inner')
        for item in item_catalog_menu:
            box_item = item.find_all('div', class_='CatalogCategoryMenu__box')
            for box in box_item:
                name = re.sub("^\s+|\n|\r|\r|\s+$", '', box.contents[0].contents[0])
                if first_change:
                    self.CATEGORY_LIST.insert(index, name)
                    index += 1
                else:
                    self.CATEGORY_LIST[index] = name
                    index += 1
                    first_change = True
                list_href_menu_item.append(box.contents[0].attrs['href'])
        for url in list_href_menu_item:
            r = requests.get(url, headers=headers)
            bs = BeautifulSoup(r.text, "html.parser")
            page_widget = bs.find_all('a', class_='PaginationWidget__page')
            # if not page_widget:
            #     print(0)
            # else:
            #     print(page_widget[page_widget.__len__()-1].attrs['data-page'])

    def parser_on_page(self, page_widget, bs, headers, url):
        page_widget = 1
        id = 0
        # функция получает информацию о товарах из указанной категории
        item_on_page = bs.find('section', class_='ProductGroupList')
        for page in range(page_widget):
            url_on_page = url + '?p=' + str(page+1)
            req = requests.get(url_on_page, headers=headers)
            bs = BeautifulSoup(req.text, "html.parser")
            item_widget = bs.find('section', class_='ProductGroupList')
            for item in item_widget:
                if item.find('div', class_='ProductCardHorizontal__not-available-block'):
                    continue
                if item.name != 'div':
                    continue
                name_product_title = item.find('a', class_='ProductCardHorizontal__title')
                image_product_url = item.find('div', class_='ProductCardHorizontal__picture-hover_part')
                product_price = item.find('span', class_='ProductCardHorizontal__price_current-price')
                name_product_title = name_product_title.contents[0]
                image_product_url = image_product_url.attrs['data-src']
                product_price = re.sub("^\s+|\n|\r|\r|\s+$", '', product_price.contents[0]) + '$'
                self.PRODUCT.update({id: {"name": name_product_title, 'url_img': image_product_url, 'price': product_price}})
                id += 1

    def parser_product(self, headers):
        # Функция для парсинга товаров
        page = 0
        for url in self.CATEGORY_HREF:
            r = requests.get(url, headers=headers)
            bs = BeautifulSoup(r.text, "html.parser")
            page_widget = bs.find_all('a', class_='PaginationWidget__page')
            if not page_widget:
                self.parser_catalog_menu(bs, self.CATEGORY_HREF.index(url), headers)
            else:
                count_page = page_widget[page_widget.__len__() - 1].attrs['data-page']
                return self.parser_on_page(count_page, bs, headers, url)

    def parser_citilink(self):
        # Метод настраивает парсинг сайта и который получает и обрабатывает полученную информацию с сайта Citilink
        url = "https://www.citilink.ru/catalog/"
        headers = {"Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"}
        r = requests.get(url, headers=headers)
        bs = BeautifulSoup(r.text, "html.parser")
        self.parser_catalog_and_category_product(bs)
        self.parser_product(headers)
