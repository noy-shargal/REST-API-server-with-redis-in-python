from datetime import datetime
import uuid

import redis

from .models import Message, MessagesList

uuid_length_with_dot = 37


class RedisDatabase:
    """ Redis database to store messages """

    def __init__(self, db):
        self.__redis = redis.StrictRedis(host='messages_redis', port=6379, db=int(db), charset='utf-8',
                                         decode_responses=True)

    def publish_message(self, message) -> None:
        """
        Add a new message to Redis

        A sorted set is used to store messages
        key     = the name of the set
        score   = the timestamp
        value   = the message with a uuid appended
        """

        # Create a timestamp of the current time
        message_timestamp = int(datetime.now().timestamp())

        # Append a uuid to the message
        message_with_uid = message + '.' + str(uuid.uuid4())

        # Add the message to a sorted set
        self.__redis.zadd(name='messages', mapping={message_with_uid: message_timestamp})

    def get_last_message(self) -> Message:
        """
        Get the last message added to Redis
        """

        try:
            content = self.__redis.zrevrangebyscore(name='messages', min='-inf', max='+inf', start=0, num=1)[0]
            # Remove uuid
            content = content[:-uuid_length_with_dot]

            message = Message(content=content)
        except (redis.exceptions.DataError, IndexError):
            message = Message(content='')

        return message

    def get_message_by_time(self, date) -> MessagesList:
        """
        Get messages between dates from Redis
        """

        # Create timestamps from dates
        try:
            date_time_start = int(datetime.strptime(date.start, '%Y-%m-%dT%H:%M:%S').timestamp())
            date_time_end = int(datetime.strptime(date.end, '%Y-%m-%dT%H:%M:%S').timestamp())
        except ValueError:
            return MessagesList(messages=[])

        # Fetch all the messages between the dates
        contents = self.__redis.zrangebyscore('messages', date_time_start, date_time_end)
        messages_list = MessagesList(messages=[])
        for content in contents:
            # Remove uuid
            content = content[:-uuid_length_with_dot]

            message = Message(content=content)
            messages_list.messages.append(message)

        return messages_list

    def flush_db(self):
        """ Flush Redis database """

        self.__redis.flushdb()
