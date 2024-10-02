"""Основной модуль."""

from db_setup import create_sku_table

from xml_parse import parse_and_insert_xml

if __name__ == "__main__":
    create_sku_table()
    parse_and_insert_xml()
