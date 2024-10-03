"""Основной модуль."""

import os

from db_setup import create_sku_table

from same_sku import same_sku_start

from xml_parse import parse_and_insert_xml


MAX_TAGS_COUNT = int(os.getenv("MAX_TAGS_COUNT"))


if __name__ == "__main__":
    create_sku_table()

    parse_and_insert_xml(MAX_TAGS_COUNT)

    same_sku_start()
