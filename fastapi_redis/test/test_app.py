import pytest
import datetime
from fastapi.testclient import TestClient

import redis

from ..app import app, common_parameters
from ..redis_database import RedisDatabase
from ..models import Date

client = TestClient(app)

# db = 1 for testing
db = 1


async def override_dependency():
    return {'db': db}


app.dependency_overrides[common_parameters] = override_dependency


class TestApp:

    def test_api_publish_1(self):
        """ Test the api/publish endpoint """

        client.post("/api/publish", json={'content': 'message123'})
        response = client.post("/api/publish", json={'content': 'message1234'})

        assert response.status_code == 201
        assert response.json() == {"success": "new message added"}

    def test_api_getlast_1(self):
        """ Test the api/getlast endpoint """

        response = client.get("/api/getlast")

        assert response.status_code == 200
        assert response.json() == {"content": "message1234"}

    def test_api_publish_2(self):
        """ Test the api/publish endpoint """

        client.post("/api/publish", json={'content': 'this is a message.'})
        response = client.post("/api/publish", json={'content': 'this is a message.'})

        assert response.status_code == 201
        assert response.json() == {"success": "new message added"}

    def test_api_getlast_2(self):
        """ Test the api/getlast endpoint """

        response = client.get("/api/getlast")

        assert response.status_code == 200
        assert response.json() == {"content": "this is a message."}

    def test_api_getbytime(self):
        """ Test the api/getbytime endpoint """

        now = datetime.datetime.now()
        now_str = datetime.datetime.strftime(now, '%Y-%m-%dT%H:%M:%S')

        one_hour_into_future = now + datetime.timedelta(hours=1)
        one_hour_into_future_str = datetime.datetime.strftime(one_hour_into_future, '%Y-%m-%dT%H:%M:%S')

        request_data = {'start': now_str, 'end': one_hour_into_future_str}
        response_data = {
            'messages': [{'content': 'message123'}, {'content': 'message1234'}, {'content': 'this is a message.'},
                         {'content': 'this is a message.'}]}

        response = client.get("/api/getbytime/", json=request_data)

        assert response.status_code == 200
        assert response.json() == response_data

    def test_api_getlast_no_message(self):
        """ Test the api/getlast endpoint when no message was found """

        redis_database = RedisDatabase(db=db)
        redis_database.flush_db()

        response = client.get("/api/getlast")

        assert response.status_code == 404
        assert response.json() == {"detail": "no message found"}

    def test_api_getbytime_no_message(self):
        """ Test the api/getbytime endpoint when no messages was found """

        redis_database = RedisDatabase(db=db)
        redis_database.flush_db()

        now = datetime.datetime.now()
        now_str = datetime.datetime.strftime(now, '%Y-%m-%dT%H:%M:%S')

        one_hour_into_future = now + datetime.timedelta(hours=1)
        one_hour_into_future_str = datetime.datetime.strftime(one_hour_into_future, '%Y-%m-%dT%H:%M:%S')

        request_data = {'start': now_str, 'end': one_hour_into_future_str}

        response = client.get("/api/getbytime", json=request_data)

        assert response.status_code == 404
        assert response.json() == {"detail": "no messages found"}

    def test_publish_message(self):
        """ Test the publish message function """

        redis_database = RedisDatabase(db=db)
        redis_database.publish_message('message1')

        r = redis.StrictRedis(host='messages_redis', port=6379, db=db, charset='utf-8', decode_responses=True)
        content = r.zrevrangebyscore(name='messages', min='-inf', max='+inf', start=0, num=1)[0]
        uuid_length_with_dot = 37
        content = content[:-uuid_length_with_dot]

        assert content == "message1"

    def test_get_last_message(self):
        """ Test the get last message function """

        redis_database = RedisDatabase(db=db)
        redis_database.publish_message('message2')
        redis_database.publish_message('message3')

        last_message = redis_database.get_last_message()

        assert last_message.content == "message3"

    def test_get_message_by_time(self):
        """ Test the get message by time function """

        redis_database = RedisDatabase(db=db)
        redis_database.publish_message('message4')
        redis_database.publish_message('message5')

        now = datetime.datetime.now()
        now_str = datetime.datetime.strftime(now, '%Y-%m-%dT%H:%M:%S')

        one_hour_into_future = now + datetime.timedelta(hours=1)
        one_hour_into_future_str = datetime.datetime.strftime(one_hour_into_future, '%Y-%m-%dT%H:%M:%S')

        date = Date(start=now_str, end=one_hour_into_future_str)

        messages_list = redis_database.get_message_by_time(date)

        assert 5 == len(messages_list.messages)

    def test_get_message_by_time_no_messages_found(self):
        """ Test the get message by time function when no messages are found """

        redis_database = RedisDatabase(db=db)
        redis_database.publish_message('message6')
        redis_database.publish_message('message7')

        now = datetime.datetime.now()
        one_hour_into_future = now + datetime.timedelta(hours=1)
        two_hour_into_future = now + datetime.timedelta(hours=2)
        one_hour_into_future_str = datetime.datetime.strftime(one_hour_into_future, '%Y-%m-%dT%H:%M:%S')
        two_hour_into_future_str = datetime.datetime.strftime(two_hour_into_future, '%Y-%m-%dT%H:%M:%S')

        date = Date(start=one_hour_into_future_str, end=two_hour_into_future_str)

        messages_list = redis_database.get_message_by_time(date)

        assert 0 == len(messages_list.messages)


@pytest.fixture(scope='session', autouse=True)
def db_cleanup():
    """ Cleanup """

    yield
    redis_database = RedisDatabase(db=db)
    redis_database.flush_db()
