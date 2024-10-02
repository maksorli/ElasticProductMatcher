"""Модуль для настройки базы данных и инициализации таблиц."""

import logging
import os

from dotenv import load_dotenv

import psycopg2


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")


# SQL скрипт для создания таблицы SKU
create_table_query = """
CREATE TABLE IF NOT EXISTS public.sku
(
    uuid UUID PRIMARY KEY,
    marketplace_id INTEGER DEFAULT 0,
    product_id BIGINT DEFAULT 0,
    title TEXT,
    description TEXT,
    brand TEXT,
    seller_id INTEGER  DEFAULT 0,
    seller_name TEXT,
    first_image_url TEXT,
    category_id INTEGER  DEFAULT 0,
    category_lvl_1 TEXT,
    category_lvl_2 TEXT,
    category_lvl_3 TEXT,
    category_remaining TEXT,
    features JSON,
    rating_count INTEGER DEFAULT 0,
    rating_value DOUBLE PRECISION DEFAULT 0.0,
    price_before_discounts REAL DEFAULT 0.0,
    discount DOUBLE PRECISION DEFAULT 0.0,
    price_after_discounts REAL DEFAULT 0.0,
    bonuses INTEGER DEFAULT 0,
    sales INTEGER DEFAULT 0,
    inserted_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    currency TEXT,
    barcode BIGINT DEFAULT 0,
    similar_sku UUID[]
);
"""


def create_sku_table():
    """Подключение к базе данных и создание таблицы SKU."""
    try:
        # Подключение к PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
        )
        cur = conn.cursor()
        # Логируем попытку создания таблицы
        logging.info("Попытка создания таблицы SKU...")

        # Выполнение SQL-запроса
        cur.execute(create_table_query)
        conn.commit()

        logging.info("Таблица SKU успешно создана!")
        cur.close()
        conn.close()

    except Exception as e:
        # Логируем ошибку при подключении к базе данных
        logging.error(f"Ошибка при подключении к БД: {e}")
