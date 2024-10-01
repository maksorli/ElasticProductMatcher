"""Модуль для парсинга xml."""

import logging
import os
import uuid
from io import BufferedReader

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
    "http://export.admitad.com/ru/webmaster/websites/:"
    "777011/products/export_adv_products/?user=bloggings"
    "_style&code=uzztv9z1ss&feed_id=21908&format=xml"
)

insert_sku_query = """
    INSERT INTO sku (
        uuid, marketplace_id, product_id, title, description, brand,
        seller_id, seller_name, first_image_url, category_id,
        category_lvl_1, category_lvl_2, category_lvl_3,
        category_remaining, features, rating_count, rating_value,
        price_before_discounts, discount, price_after_discounts,
        bonuses, sales, barcode, similar_sku
    ) VALUES %s
"""


def parse_and_insert_xml():
    """Функция для парсинга XML-файла и вставки данных в PostgreSQL."""
    tags_count = 0
    max_tags_count = 50
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
            buffered_response = BufferedReader(response.raw)
            context = etree.iterparse(
                buffered_response, events=("end",), tag="offer"
            )
            logging.info("получил ответ")
            # Создаем контекст для парсинга XML-файла
            context = etree.iterparse(
                response.raw, events=("end",), tag="offer"
            )
            logging.info("распарсил")
            for _, elem in context:
                try:
                    # Парсинг тега'offer'
                    product_id = int(elem.get("id", 0))
                    title = elem.findtext("name", default="")
                    description = elem.findtext("description", default="")
                    brand = elem.findtext("vendor", default="")
                    category_id = int(
                        elem.findtext("categoryId", default=None)
                    )
                    price_before_discounts = float(
                        elem.findtext("oldprice", default=None)
                    )
                    price = float(elem.findtext("price", default=0))
                    # Генерация SKU данных
                    sku_data = (
                        uuid.uuid4(),  # Генерируем UUID
                        1,  # marketplace_id
                        product_id,
                        title,
                        description,
                        brand,
                        None,  # seller_id
                        None,  # seller_name
                        None,  # first_image_url
                        category_id,
                        None,  # category_lvl_1
                        None,  # category_lvl_2
                        None,  # category_lvl_3
                        None,  # category_remaining
                        None,  # features
                        None,  # rating_count
                        None,  # rating_value
                        price_before_discounts,
                        None,  # discount
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
                    if tags_count >= max_tags_count:
                        break

                except Exception as e:
                    logging.error(
                        f"Ошибка при обработке товара {product_id}: {e}"
                    )

                finally:
                    # Очищаем элемент для освобождения памяти
                    elem.clear()
                    while elem.getprevious() is not None:
                        del elem.getparent()[0]

            # Закрытие курсора и соединения с базой данных
            cur.close()
            conn.close()

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при загрузке XML: {e}")
    except etree.XMLSyntaxError as e:
        logging.error(f"Ошибка парсинга XML: {e}")
    except psycopg2.DatabaseError as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
    except Exception as e:
        logging.error(f"Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    parse_and_insert_xml()
