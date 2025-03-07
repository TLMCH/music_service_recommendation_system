import requests
import logging
import pandas as pd

recommendations_url = "http://127.0.0.1:8000"
events_store_url = "http://127.0.0.1:8020"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

user_id = 567
event_item_ids =  [99262, 590262, 590303, 590692, 43527461]
 
for event_item_id in event_item_ids:
    resp = requests.post(events_store_url + "/put", 
                         headers=headers, 
                         params={"user_id": user_id, "track_id": event_item_id})
                         
params = {"user_id": user_id, 'k': 5}
resp_top = requests.post(recommendations_url + "/recommendations_top", headers=headers, params=params)
resp_offline = requests.post(recommendations_url + "/recommendations_offline", headers=headers, params=params)
resp_blended = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)

recs_top = resp_top.json()["recs"]
recs_offline = resp_offline.json()["recs"]
recs_blended = resp_blended.json()["recs"]

print(recs_top[0])
print(recs_offline[0])
print(recs_blended)

# Код для отображения названия треков
# Чтобы загрузить catalog_names в локальный репозиторий введите команду: wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet
catalog_names = pd.read_parquet('catalog_names.parquet')
def fill_id(row, type):
    return int(row['id']) if row['type'] == type else None
catalog_names['track_id'] = catalog_names.apply(lambda row: fill_id(row, 'track'), axis=1)

logging.basicConfig(level=logging.INFO, filename="test_service.log",filemode="w")

logging.info(recs_top[0])
recs_top_text = ""
for i in recs_top[0]:
    track = catalog_names[catalog_names['track_id'] == i]['name'].tolist()[0]
    recs_top_text += track + ', '
logging.info(recs_top_text)

logging.info(recs_offline[0])
recs_offline_text = ""
for i in recs_offline[0]:
    track = catalog_names[catalog_names['track_id'] == i]['name'].tolist()[0]
    recs_offline_text += track + ', '
logging.info(recs_offline_text)

logging.info(recs_blended)
recs_blended_text = ""
for i in recs_blended:
    track = catalog_names[catalog_names['track_id'] == i]['name'].tolist()[0]
    recs_blended_text += track + ', '
logging.info(recs_blended_text)