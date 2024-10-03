# ElasticProductMatcher
MarketplaceSync — это сервис для обработки и загрузки данных товаров из маркетплейсов в базу данных PostgreSQL и Elasticsearch
# Используемые библиотеки
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue?style=flat&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-20.10-blue?style=flat&logo=docker)
![lxml](https://img.shields.io/badge/lxml-5.3.0-blue)
![black](https://img.shields.io/badge/black-24.8.0-black?style=flat&logo=python)
![elasticsearch](https://img.shields.io/badge/elasticsearch-8.15.1-blue?logo=elasticsearch&logoColor=white)

## Описание проекта
Этот проект представляет собой сервис, который:

Загружает товары из XML-файла маркетплейса, расположенного по этой ссылке, и сохраняет их в базу данных PostgreSQL.

Разворачивает Elasticsearch с помощью Docker Compose для дальнейшего поиска и анализа товаров.

Индексирует товары в Elasticsearch, а затем для каждого товара находит до 5 наиболее похожих товаров и сохраняет их UUID в поле similar_sku в базе данных.


Решение проблемы с большим файлом
Поскольку исходный XML-файл имеет размер более 5 ГБ, его чтение целиком в память невозможно. Для эффективной обработки файла используется итеративный парсинг с помощью lxml.etree.iterparse, что позволяет считывать и обрабатывать данные по частям.



 ## Установка и запуск

1. Склонируйте репозиторий:

   ```bash
   git clone https://github.com/maksorli/ElasticProductMatcher.git
   

2. Проверьте версию Docker и Docker Compose, либо установите:
    ```bash
    docker --version
    docker-compose --version
    
3. Создайте файл .env  с переменными окружения (пример: .env.example)
    ```bash
        # Параметры подключения к базе данных
    DB_NAME = elastic
    DB_USER = elastic_user
    DB_PASSWORD = elastic123
    DB_HOST = postgres

    # указать число товаров для обработки, если присвоить 0 будет обработан весь файл.
    MAX_TAGS_COUNT = 5000  


4. Запустите проект с помощью Docker Compose:
   ```bash
   docker-compose up --build
 


## Пример результата: 
| product_uuid                             | product_title                                                              | similar_uuid                           | similar_title                                                              |
|------------------------------------------|----------------------------------------------------------------------------|----------------------------------------|----------------------------------------------------------------------------|
| 64821bdb-f06e-453a-b368-18ec61c5bee4     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Главное фыр-фыр  | 1415b9ad-42a2-406d-8c27-033b4b64a5f7   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Восход 11        |
| 64821bdb-f06e-453a-b368-18ec61c5bee4     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Главное фыр-фыр  | 293f6b98-28f3-4576-bf4d-bfdab1c5fc53   | Чехол на Huawei Y5p / Хуавей Y5p с принтом Главное фыр-фыр                 |
| 64821bdb-f06e-453a-b368-18ec61c5bee4     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Главное фыр-фыр  | 5232aab1-605b-4bc0-bff8-806e35ee208f   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом IBM             |
| 64821bdb-f06e-453a-b368-18ec61c5bee4     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Главное фыр-фыр  | 56a59dbf-53bc-4ec7-969e-88c0faaae587   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про прозрачный               |
| 64821bdb-f06e-453a-b368-18ec61c5bee4     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Главное фыр-фыр  | df298850-6341-456c-a949-bb57a3272c03   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Горы 11         |
| 3bb1bc25-6215-4db2-8dd9-a7bd05d4455b     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Голубые клематисы, прозрачный | 3926a469-c9e9-4d00-96bd-2224231dcc37   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Мышка, прозрачный |
| 3bb1bc25-6215-4db2-8dd9-a7bd05d4455b     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Голубые клематисы, прозрачный | 530dfb71-2926-46fb-91aa-9afa627117d1   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Голубая ящерка  |
| 3bb1bc25-6215-4db2-8dd9-a7bd05d4455b     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Голубые клематисы, прозрачный | 555f2a6c-af8e-4045-bab1-d1177cc0090a   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом На счастье, прозрачный |
| 3bb1bc25-6215-4db2-8dd9-a7bd05d4455b     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Голубые клематисы, прозрачный | 56a59dbf-53bc-4ec7-969e-88c0faaae587   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про прозрачный               |
| 3bb1bc25-6215-4db2-8dd9-a7bd05d4455b     | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Голубые клематисы, прозрачный | 6dea45c9-045f-4456-81be-99f49c606c37   | Чехол на Huawei Nova 11 Pro / Хуавей Нова 11 Про с принтом Голубой мрамор рисунок |
| 9c23ef2c-206c-4b5f-ba92-5847f029a5a6     | 55" Телевизор LG 55UR78001LJ 2023 VA, черный                               | 9250ea27-03fb-4ac7-ba55-292117237b0a   | 55" Телевизор LG OLED55B2RLA 2022 OLED, маренго                          |
| 9c23ef2c-206c-4b5f-ba92-5847f029a5a6     | 55" Телевизор LG 55UR78001LJ 2023 VA, черный                               | cf8a8467-fb3d-4b4b-a7f5-6c21a2f3cbfc   | 65" Телевизор LG 65NANO756QA 2022 IPS, черный                            |
| 81be25d6-4e23-42fd-bf0f-01293eba9f6c     | Смартфон Samsung Galaxy S21 FE 8/256 ГБ, Dual nano SIM, зеленый             | 29f49f9d-7dc2-4f75-94fe-456794080782   | Смартфон Samsung Galaxy S22+ 8/256 ГБ, Dual: nano SIM + eSIM, розовый     |
| 81be25d6-4e23-42fd-bf0f-01293eba9f6c     | Смартфон Samsung Galaxy S21 FE 8/256 ГБ, Dual nano SIM, зеленый             | 9b994d04-e5e4-40f4-a0a3-dbfcfd93cfef   | Смартфон Samsung Galaxy S21 FE 8/256 ГБ, Dual nano SIM, зеленый           |
| 81be25d6-4e23-42fd-bf0f-01293eba9f6c     | Смартфон Samsung Galaxy S21 FE 8/256 ГБ, Dual nano SIM, зеленый             | a6785d6b-2f44-4af2-bd74-0cd40685705b   | Смартфон Samsung Galaxy S22+ 8/256 ГБ, Dual nano SIM, розовый            |
| 81be25d6-4e23-42fd-bf0f-01293eba9f6c     | Смартфон Samsung Galaxy S21 FE 8/256 ГБ, Dual nano SIM, зеленый             | b18b9b7c-ae41-4832-ba16-c1703c6d7517   | Смартфон Samsung Galaxy S21 FE 8/256 ГБ, Dual nano SIM, зеленый           |
| 81be25d6-4e23-42fd-bf0f-01293eba9f6c     | Смартфон Samsung Galaxy S21 FE 8/256 ГБ, Dual nano SIM, зеленый             | b36410b2-b748-4fee-9660-e55b2827140e   | Смартфон Samsung Galaxy S22+ 8/256 ГБ, Dual nano SIM, зеленый            |
| 1dc2c68d-22ab-464c-9f3f-f8d0387a1fb6     | 43" Телевизор artel UA43H3401 2019, стальной                               | 48e8e8e1-9eb6-47fb-88ac-fd3ca64c1805   | 43" Телевизор Asano 43LU8130S IPS, черный                               |
| 1dc2c68d-22ab-464c-9f3f-f8d0387a1fb6     | 43" Телевизор artel UA43H3401 2019, стальной                               | 564bd14c-5f23-4aae-9ca7-1d18dfb34975   | 50" Телевизор artel UA50H3502 2020, темно-серый                         |
| 1dc2c68d-22ab-464c-9f3f-f8d0387a1fb6     | 43" Телевизор artel UA43H3401 2019, стальной                               | 97f080a5-e5d9-4207-9629-f9df16e2f800   | 43" Телевизор LG 43UR81006LJ 2023 VA RU, черный                         |
| 1dc2c68d-22ab-464c-9f3f-f8d0387a1fb6     | 43" Телевизор artel UA43H3401 2019, стальной                               | efac1cb3-6f18-4860-834b-171688dafef8   | 32" Телевизор artel UA32H3200, черный/серый                             |
| 1dc2c68d-22ab-464c-9f3f-f8d0387a1fb6     | 43" Телевизор artel UA43H3401 2019, стальной                               | fa584ef1-b5e5-4fdf-91c9-82baf2ef2938   | 32" Телевизор Olto 32T20H 2019, черный                                  |
| 68e637c4-74e4-455e-bd7c-3fc8b8b9b245     | 32" Телевизор JVC LT-32M395 2020 IPS, черный                               | 14d522c3-40aa-4c9f-b3e3-6f0015b266e7   | 65" Телевизор HARPER 65U770TS 2020 IPS, черный                           |
| 68e637c4-74e4-455e-bd7c-3fc8b8b9b245     | 32" Телевизор JVC LT-32M395 2020 IPS, черный                               | 75e04c99-ffb9-4d03-8632-df9601ae3410   | Пульт ДУ Huayu RM-C2020 для JVC                                           |
| 68e637c4-74e4-455e-bd7c-3fc8b8b9b245     | 32" Телевизор JVC LT-32M395 2020 IPS, черный                               | c8dd2980-0261-4a9d-a620-c67559f03f74   | Пульт HUAYU для телевизора JVC LT-22M440W                                 |
| 68e637c4-74e4-455e-bd7c-3fc8b8b9b245     | 32" Телевизор JVC LT-32M395 2020 IPS, черный                               | d46fc6e5-1b76-4307-9c1b-9a541b2e0508   | 40" Телевизор JVC LT-40M690 2020 IPS, черный                             |
| 68e637c4-74e4-455e-bd7c-3fc8b8b9b245     | 32" Телевизор JVC LT-32M395 2020 IPS, черный                               | e7f21070-e504-465d-9793-53b8d64452ce   | Пульт для телевизора JVC LT-40M640                                       |
| 80b7bd9c-011c-492f-8321-3f639122a3c1     | Умная колонка Apple HomePod mini (без часов), белый                         | 0c947514-766e-4410-8dac-3774ecc9a09d   | Стационарная акустика Apple Умная колонка HomePod mini, оранжевый         |
| 80b7bd9c-011c-492f-8321-3f639122a3c1     | Умная колонка Apple HomePod mini (без часов), белый                         | 3cfcc5b4-6c62-4edc-b671-9b3bfe7641f5   | Умная колонка Apple HomePod mini (без часов), синий                      |
| 80b7bd9c-011c-492f-8321-3f639122a3c1     | Умная колонка Apple HomePod mini (без часов), белый                         | 77785326-9e69-41fa-afeb-0a1531969214   | Умная колонка Apple HomePod mini (без часов), желтый                     |
| 80b7bd9c-011c-492f-8321-3f639122a3c1     | Умная колонка Apple HomePod mini (без часов), белый                         | 8a5a1b1b-787c-440c-9b24-382e957d7452   | Умная колонка Apple HomePod mini (без часов), оранжевый                  |
| 80b7bd9c-011c-492f-8321-3f639122a3c1     | Умная колонка Apple HomePod mini (без часов), белый                         | 8fb9a4de-a54e-4705-ae9a-f7aa29397275   | Умная колонка Apple HomePod mini (без часов), синий                      |
| 3cfcc5b4-6c62-4edc-b671-9b3bfe7641f5     | Умная колонка Apple HomePod mini (без часов), синий                         | 0c947514-766e-4410-8dac-3774ecc9a09d   | Стационарная акустика Apple Умная колонка HomePod mini, оранжевый         |
| 3cfcc5b4-6c62-4edc-b671-9b3bfe7641f5     | Умная колонка Apple HomePod mini (без часов), синий                         | 77785326-9e69-41fa-afeb-0a1531969214   | Умная колонка Apple HomePod mini (без часов), желтый                     |
| 3cfcc5b4-6c62-4edc-b671-9b3bfe7641f5     | Умная колонка Apple HomePod mini (без часов), синий                         | 80b7bd9c-011c-492f-8321-3f639122a3c1   | Умная колонка Apple HomePod mini (без часов), белый                      |
| 3cfcc5b4-6c62-4edc-b671-9b3bfe7641f5     | Умная колонка Apple HomePod mini (без часов), синий                         | 8a5a1b1b-787c-440c-9b24-382e957d7452   | Умная колонка Apple HomePod mini (без часов), оранжевый                  |
| 3cfcc5b4-6c62-4edc-b671-9b3bfe7641f5     | Умная колонка Apple HomePod mini (без часов), синий                         | 8fb9a4de-a54e-4705-ae9a-f7aa29397275   | Умная колонка Apple HomePod mini (без часов), синий                      |
| 564bd14c-5f23-4aae-9ca7-1d18dfb34975     | 50" Телевизор artel UA50H3502 2020, темно-серый                             | 1dc2c68d-22ab-464c-9f3f-f8d0387a1fb6   | 43" Телевизор artel UA43H3401 2019, стальной                             |
| 564bd14c-5f23-4aae-9ca7-1d18dfb34975     | 50" Телевизор artel UA50H3502 2020, темно-серый                             | 97ed2ec4-14e8-4dd6-a82b-52d959621809   | Телевизор Grundig 50 GFU 7800B                                            |
| 564bd14c-5f23-4aae-9ca7-1d18dfb34975     | 50" Телевизор artel UA50H3502 2020, темно-серый                             | e24308d8-90ab-4c63-8129-84803e01d7e6   | Ремешок для часов Garmin, нейлоновый, шириной 20 мм, темно-серый          |
| 564bd14c-5f23-4aae-9ca7-1d18dfb34975     | 50" Телевизор artel UA50H3502 2020, темно-серый                             | efac1cb3-6f18-4860-834b-171688dafef8   | 32" Телевизор artel UA32H3200, черный/серый                             |
| 564bd14c-5f23-4aae-9ca7-1d18dfb34975     | 50" Телевизор artel UA50H3502 2020, темно-серый                             | effb0a7a-6cfb-45dc-91b7-78a9747ca211   | Фотофон1,4х2 м темно-серый "Relief" для художественной фотографии       |
