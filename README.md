# Проект: Создание рекомендательной системы для музыкального сервиса.

Цель проекта — разработка прототипа рекомендательной системы для музыкального сервиса. Основная задача — создание персонализированной рекомендательной системы, способной на основе исторических взаимодействий пользователей с треками формировать релевантные музыкальные рекомендации.

Проект направлен не на оптимизацию моделей или подбор гиперпараметров, а на построение рабочего пайплайна, который может генерировать персональные рекомендации на основе пользовательских взаимодействий с музыкальным каталогом.
ис, предоставляющий пользователю рекомендованный музыкальный контент.

### Загрузка файлов с данными

В этом проекте используются три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Для удобства можно воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

### Структура проекта:

- configurations.py - файл с адресами сервисов

- events_service.py - сервис сохраняющий взаимодействия пользователей с треками

- features_service.py - сервис возвращающий список похожих объектов длиной k для песни по track_id

- recommendations.ipynb - файл с проведением EDA и построением рекомендаций

- recommendations.py - файл с классом для выдачи персональных рекомендаций

- recommendations_service.py - основной сервис выдачи рекомендаций

- test_notebook.ipynb - в этом ноутбуке мжно посмотреть какие идентификаторы есть в таблицах и узнать какие песни рекомендовала модель

- test_service.log - логи тестировочного скрипта

- test_service.py - скрипт для тестрования сервиса выдачи рекомендаций

### Команды для запуска сервисов:
~~~
uvicorn recommendations_service:app 
~~~
~~~
uvicorn features_service:app --port 8010
~~~
~~~
uvicorn events_service:app --port 8020 
~~~

### Команда для запуска тестировочного скрипта:
~~~
python3 test_service.py
~~~
