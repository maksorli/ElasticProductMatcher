"""Модуль для парсинга xml."""

import logging
import os
import uuid

from dotenv import load_dotenv

from lxml import etree

import psycopg2
from psycopg2.extras import execute_values

import requests


# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Переменные окружения для подключения к базе данных
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")

# URL XML-файла
XML_FILE_URL = (
    "http://export.admitad.com/ru/webmaster/websites/"
    "777011/products/export_adv_products/?user=bloggings"
    "_style&code=uzztv9z1ss&feed_id=21908&format=xml"
)

insert_sku_query = """
    INSERT INTO public.sku (
        uuid, marketplace_id, product_id, title, description, brand,
        seller_id, seller_name, first_image_url, category_id,
        category_lvl_1, category_lvl_2, category_lvl_3,
        category_remaining, features, rating_count, rating_value,
        price_before_discounts, discount, price_after_discounts,
        bonuses, sales, barcode, similar_sku
    ) VALUES %s
"""


def parse_and_insert_xml(max_count=0):
    """Функция для парсинга XML-файла и вставки данных в PostgreSQL."""
    tags_count = 0
    max_count = max_count
    try:
        # Установка соединения с базой данных
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
        )
        cur = conn.cursor()

        # Загрузка XML-файла через HTTP с потоковой передачей
        with requests.get(XML_FILE_URL, stream=True) as response:
            response.raise_for_status()  # Проверяем успешность запроса
            response.raw.decode_content = True
            logging.info("получил ответ")
            # Создаем контекст для парсинга XML-файла
            context = etree.iterparse(response.raw, events=("start", "end"))
            category_dict = {}
            in_categories = False
            in_offers = False
            if max_count > 0:
                logging.info(f"Начат парсинг {max_count} товаров")
            if max_count == 0:
                logging.info("Начат парсинг всего файла")
            for event, elem in context:
                if event == "start":
                    if elem.tag == "categories":
                        in_categories = True
                    elif elem.tag == "offers":
                        in_offers = True
                elif event == "end":
                    if elem.tag == "category" and in_categories:
                        # Обработка категории
                        category_id = elem.get("id")
                        parent_id = elem.get("parentId")
                        name = elem.text.strip() if elem.text else ""
                        category_dict[category_id] = {
                            "name": name,
                            "parentId": parent_id,
                        }
                        elem.clear()
                    elif elem.tag == "categories" and in_categories:
                        in_categories = False
                        logging.info(
                            f"Разобрано {len(category_dict)} категорий."
                        )
                    elif elem.tag == "offer" and in_offers:
                        # Обработка предложения
                        try:
                            # Парсинг тега 'offer'
                            product_id = int(elem.get("id", 0))
                            title = elem.findtext("name", default="")
                            description = elem.findtext(
                                "description", default=""
                            )
                            brand = elem.findtext("vendor", default="")
                            category_id = elem.findtext(
                                "categoryId", default=None
                            )
                            price_element = elem.find("price")
                            if (
                                price_element is not None
                                and price_element.text
                            ):
                                price = float(price_element.text)
                            else:
                                price = 0.0

                            price_before_discounts_element = elem.find(
                                "price_before_discounts"
                            )
                            if (
                                price_before_discounts_element is not None
                                and price_before_discounts_element.text
                            ):
                                price_before_discounts = float(
                                    price_before_discounts_element.text
                                )
                            else:
                                # Если нет цены до скидки, берем текущую цену
                                price_before_discounts = price
                            discount = None
                            if (
                                price
                                and price_before_discounts
                                and price >= price_before_discounts
                            ):
                                discount = (
                                    (price_before_discounts - price)
                                    / price_before_discounts
                                    * 100
                                )
                                discount = round(discount, 2)

                            # Построение пути категории
                            category_path = []
                            current_id = category_id
                            while (
                                current_id is not None
                                and current_id in category_dict
                            ):
                                category_info = category_dict[current_id]
                                category_name = category_info["name"]
                                category_path.insert(0, category_name)
                                current_id = category_info["parentId"]
                            # Заполнение уровней категории
                            category_lvl_1 = (
                                category_path[0]
                                if len(category_path) > 0
                                else None
                            )
                            category_lvl_2 = (
                                category_path[1]
                                if len(category_path) > 1
                                else None
                            )
                            category_lvl_3 = (
                                category_path[2]
                                if len(category_path) > 2
                                else None
                            )
                            if len(category_path) > 3:
                                category_remaining = "/".join(
                                    category_path[3:]
                                )
                            else:
                                category_remaining = None

                            sku_data = (
                                str(uuid.uuid4()),  # Генерируем UUID
                                1,  # marketplace_id
                                product_id,
                                title,
                                description,
                                brand,
                                None,  # seller_id
                                None,  # seller_name
                                None,  # first_image_url
                                category_id,
                                category_lvl_1,
                                category_lvl_2,
                                category_lvl_3,
                                category_remaining,
                                None,  # features
                                None,  # rating_count
                                None,  # rating_value
                                price_before_discounts,
                                discount,  # discount
                                price,  #
                                None,  # bonuses
                                None,  # sales
                                None,  # barcode
                                [],  # similar_sku
                            )

                            # Вставка данных в базу данных
                            execute_values(
                                cur,
                                insert_sku_query,
                                [sku_data],
                            )

                            # Фиксация транзакции
                            conn.commit()

                            tags_count += 1
                            if max_count > 0 and tags_count >= max_count:
                                logging.info(
                                    f"Парсинг {max_count} товаров завершен"
                                )
                                break

                        except Exception as e:
                            logging.error(
                                f"Ошибка  обработки товара {product_id}: {e}"
                            )

                        finally:
                            # Очищаем элемент для освобождения памяти
                            elem.clear()
                            while elem.getprevious() is not None:
                                del elem.getparent()[0]
                    elif elem.tag == "offers" and in_offers:
                        in_offers = False

        # Закрытие курсора и соединения с базой данных
        cur.close()
        conn.close()

    except Exception as e:
        logging.error(f"Ошибка при парсинге XML-файла: {e}")
