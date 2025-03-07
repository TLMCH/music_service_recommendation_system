import logging

import requests
from recommendations import Recommendations
from fastapi import FastAPI
from contextlib import asynccontextmanager 

logger = logging.getLogger("uvicorn.error")
rec_store = Recommendations()
features_store_url = "http://127.0.0.1:8010"
events_store_url = "http://127.0.0.1:8020"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")
    rec_store.load(
        "personal",
        'recommendations.parquet',
        columns=["user_id", "track_id", "rank"],
    )
    rec_store.load(
        "default",
        'top_popular.parquet',
        columns=["track_id"],
    )
    yield
    # этот код выполнится только один раз при остановке сервиса
    logger.info("Stopping")
    rec_store.stats()
    
# создаём приложение FastAPI
app = FastAPI(title="recommendations", lifespan=lifespan)


@app.post("/recommendations_top")
async def recommendations_top(user_id: int, k: int = 5):
    """
    Возвращает список офлайн-рекомендаций длиной k для пользователя user_id
    """
    recs = [rec_store.get_default(user_id, k)]

    return {"recs": recs}


@app.post("/recommendations_offline")
async def recommendations_offline(user_id: int, k: int = 5):
    """
    Возвращает список офлайн-рекомендаций длиной k для пользователя user_id
    """
    recs = [rec_store.get_personal(user_id, k)]

    return {"recs": recs}


def dedup_ids(ids):
    """
    Дедублицирует список идентификаторов, оставляя только первое вхождение
    """
    seen = set()
    ids = [id for id in ids if not (id in seen or seen.add(id))]

    return ids


@app.post("/recommendations_online")
async def recommendations_online(user_id: int, k: int = 5):
    """
    Возвращает список онлайн-рекомендаций длиной k для пользователя user_id
    """

    headers = {"Content-type": "application/json", "Accept": "text/plain"}

    # получаем список последних событий пользователя, возьмём три последних
    params = {"user_id": user_id, "k": 5}
    resp = requests.post(events_store_url + "/get", headers=headers, params=params)
    events = resp.json()
    events = events["events"]

    # получаем список айтемов, похожих на последние пять, с которыми взаимодействовал пользователь
    items = []
    scores = []
    for item_id in events:
        # для каждого item_id получаем список похожих в similar_items
        params = {"track_id": item_id, "k": 5}
        resp_similar = requests.post(features_store_url + "/similar_items", headers=headers, params=params)
        item_similar_items = resp_similar.json()
        items += item_similar_items["track_id_2"]
        scores += item_similar_items["score"]
    # сортируем похожие объекты по scores в убывающем порядке
    # для старта это приемлемый подход
    combined = list(zip(items, scores))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    combined = [item for item, _ in combined]

    # удаляем дубликаты, чтобы не выдавать одинаковые рекомендации
    recs = dedup_ids(combined)
    recs = recs[: k]

    return {"recs": recs}



@app.post("/recommendations")
async def recommendations(user_id: int, k: int = 5):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """

    recs_offline = await recommendations_offline(user_id, k)
    recs_online = await recommendations_online(user_id, k)

    recs_offline = recs_offline["recs"][0]
    recs_online = recs_online["recs"]

    recs_blended = []

    min_length = min(len(recs_offline), len(recs_online))
    # чередуем элементы из списков, пока позволяет минимальная длина
    for i in range(min_length):
        recs_blended.append(recs_online[i])
        recs_blended.append(recs_offline[i])

    # добавляем оставшиеся элементы в конец
    recs_blended = recs_blended + recs_online[min_length:] + recs_offline[min_length:]

    # удаляем дубликаты
    recs_blended = dedup_ids(recs_blended)
    
    # оставляем только первые k рекомендаций
    recs_blended = recs_blended[: k]

    return {"recs": recs_blended}