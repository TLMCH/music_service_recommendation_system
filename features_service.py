import logging
from contextlib import asynccontextmanager
 
import pandas as pd
from fastapi import FastAPI 

logger = logging.getLogger("uvicorn.error")

class SimilarItems:

    def __init__(self):

        self._similar_items = None

    def load(self, path, **kwargs):
        """
        Загружаем данные из файла
        """

        logger.info(f"Loading data...")
        self._similar_items = pd.read_parquet(path, **kwargs)
        logger.info(f"Loaded")

    def get(self, track_id: int, k: int = 5):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = self._similar_items[self._similar_items['track_id_1'] == track_id].head(k)
            i2i = i2i[["track_id_2", "score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"track_id_2": [], "score": {}}

        return i2i

sim_items_store = SimilarItems()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    sim_items_store.load(
        "similar.parquet",
        columns=["track_id_1", "track_id_2", "score"],
    )
    logger.info("Ready!")
    # код ниже выполнится только один раз при остановке сервиса
    yield

# создаём приложение FastAPI
app = FastAPI(title="features", lifespan=lifespan)

@app.post("/similar_items")
async def recommendations(track_id: int, k: int = 5):
    """
    Возвращает список похожих объектов длиной k для track_id
    """

    i2i = sim_items_store.get(track_id, k)

    return i2i