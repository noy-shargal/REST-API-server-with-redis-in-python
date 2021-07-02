import redis.exceptions
from fastapi import FastAPI, Depends, HTTPException

from .redis_database import RedisDatabase
from .models import Message, MessagesList, Date
from fastapi import FastAPI, Response, status

app = FastAPI()

db = 0


async def common_parameters():
    return {'db': db}


@app.post('/api/publish', tags=['messages'],  status_code=200)
async def post_publish(message: Message, response: Response, commons: dict = Depends(common_parameters)):
    """ Add a new message """

    try:
        redis_database = RedisDatabase(commons.get('db'))
        redis_database.publish_message(message.content)
    except redis.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="could not connect to redis")
    response.status_code = status.HTTP_201_CREATED
    return {"success": "new message added"}


@app.get('/api/getlast', response_model=Message, tags=['messages'])
async def get_getlast(commons: dict = Depends(common_parameters)):
    """ Get last message """

    try:
        redis_database = RedisDatabase(commons.get('db'))
        message = redis_database.get_last_message()
    except redis.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="could not connect to redis")

    if message.content:
        return message
    else:
        raise HTTPException(status_code=404, detail="no message found")


@app.get('/api/getbytime', response_model=MessagesList, tags=['messages'])
async def get_getbytime(date: Date, commons: dict = Depends(common_parameters)):
    """ Get messages between dates """

    try:
        redis_database = RedisDatabase(commons.get('db'))
        messages_list = redis_database.get_message_by_time(date)
    except redis.exceptions.ConnectionError:
        raise HTTPException(status_code=500, detail="could not connect to redis")

    if len(messages_list.messages) > 0:
        return messages_list
    else:
        raise HTTPException(status_code=404, detail="no messages found")
