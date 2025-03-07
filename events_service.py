from fastapi import FastAPI

class EventStore:

    def __init__(self, max_events_per_user=5):
        self.events = {}
        self.max_events_per_user = max_events_per_user


    def put(self, user_id, track_id): 
        """
        Сохраняет событие
        """
        if user_id in self.events.keys():
            user_events = self.events[user_id] 
        else:
            user_events = []
        self.events[user_id] = [track_id] + user_events[: self.max_events_per_user]


    def get(self, user_id, k):
        """
        Возвращает события для пользователя
        """
        if user_id in self.events.keys():
            user_events = self.events[user_id][: k]
        else:
            user_events = []
        return user_events


events_store = EventStore()
# создаём приложение FastAPI
app = FastAPI(title="events")


@app.post("/put")
async def put(user_id: int, track_id: int):
    """
    Сохраняет событие для user_id, item_id
    """
    events_store.put(user_id, track_id)
    return {"result": "ok"}


@app.post("/get")
async def get(user_id: int, k: int = 5):
    """
    Возвращает список последних k событий для пользователя user_id
    """
    events = events_store.get(user_id, k)
    return {"events": events}