"""Модуль для поиска похожишь товаров."""

import logging
import os
import time

from dotenv import load_dotenv

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError

import psycopg2

from tqdm import tqdm

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

# Настройки Elasticsearch
ELASTICSEARCH_HOST = "http://elasticsearch:9200"
INDEX_NAME = "products"


def create_index(es):
    """Функция для создания индекса с маппингом."""
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    index_body = {
        "settings": {
            "analysis": {"analyzer": {"default": {"type": "russian"}}}
        },
        "mappings": {
            "properties": {
                "uuid": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "russian"},
                "description": {"type": "text", "analyzer": "russian"},
                "brand": {"type": "keyword"},
                "category_lvl_1": {"type": "keyword"},
                "category_lvl_2": {"type": "keyword"},
                "category_lvl_3": {"type": "keyword"},
            }
        },
    }
    es.indices.create(index=INDEX_NAME, body=index_body)


def load_data_to_elasticsearch(es, cursor):
    """Функция для загрузки данных в Elasticsearch."""
    cursor.execute("SELECT * FROM public.sku;")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    actions = []
    for row in tqdm(rows, desc="Indexing products to Elasticsearch"):
        data = dict(zip(columns, row))
        action = {
            "_index": INDEX_NAME,
            "_id": data["uuid"],
            "_source": {
                "uuid": data["uuid"],
                "title": data["title"],
                "description": data["description"],
                "brand": data["brand"],
                "category_lvl_1": data["category_lvl_1"],
                "category_lvl_2": data["category_lvl_2"],
                "category_lvl_3": data["category_lvl_3"],
                "features": data["features"],
                "price_after_discounts": data["price_after_discounts"],
                # Добавьте другие необходимые поля
            },
        }
        actions.append(action)

        # Отправляем данные пакетами по 1000 документов
        if len(actions) >= 1000:
            helpers.bulk(es, actions)
            actions = []

    # Индексируем оставшиеся документы
    if actions:
        helpers.bulk(es, actions)


def update_similar_sku(es, conn, cursor):
    """Функция для обновления similar_sku в базе данных."""
    cursor.execute("SELECT uuid FROM public.sku;")
    uuids = [row[0] for row in cursor.fetchall()]

    for current_uuid in tqdm(uuids, desc="Updating similar_sku for products"):
        # Elasticsearch запрос для поиска похожих товаров
        query = {
            "size": 6,
            "query": {
                "more_like_this": {
                    "fields": ["title", "description", "features"],
                    "like": [{"_index": INDEX_NAME, "_id": current_uuid}],
                    "min_term_freq": 1,
                    "min_doc_freq": 1,
                }
            },
        }

        response = es.search(index=INDEX_NAME, body=query)
        hits = response["hits"]["hits"]
        similar_uuids = [
            hit["_source"]["uuid"]
            for hit in hits
            if hit["_source"]["uuid"] != current_uuid
        ]

        # Оставляем до 5 похожих товаров
        similar_uuids = similar_uuids[:5]

        # Конвертируем  список   UUID
        similar_uuids_str = "{" + ",".join(similar_uuids) + "}"

        # Обновление поля similar_sku
        update_query = (
            "UPDATE public.sku SET similar_sku = %s::uuid[] "
            "WHERE uuid = %s;"
        )

        cursor.execute(update_query, (similar_uuids_str, current_uuid))
        conn.commit()


def wait_for_elasticsearch(host, timeout=15):
    """Функция ожидающая готовности  Elasticsearch."""
    es = Elasticsearch(hosts=[host])
    start_time = time.time()
    while True:
        try:
            if es.ping():
                logging.info("Elasticsearch готов к работе.")
                break
        except ConnectionError:
            pass

        if time.time() - start_time > timeout:
            raise TimeoutError(
                f"Нет подключения к Elasticsearch в течение {timeout} секунд."
            )
        logging.info("Ожидаем готовности Elasticsearch...")
        time.sleep(5)


def same_sku_start():
    """Функция запускающая  процесс сравнения SKU."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cursor = conn.cursor()
    wait_for_elasticsearch(ELASTICSEARCH_HOST)

    es = Elasticsearch(ELASTICSEARCH_HOST)

    # Создание индекса
    create_index(es)

    # Загрузка данных в Elasticsearch
    load_data_to_elasticsearch(es, cursor)

    # Обновление similar_sku
    update_similar_sku(es, conn, cursor)

    # Закрытие соединений
    cursor.close()
    conn.close()
