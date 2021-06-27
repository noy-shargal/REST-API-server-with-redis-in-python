from pydantic import BaseModel


class Message(BaseModel):
    """ Message model """

    content: str


class MessagesList(BaseModel):
    """ Messages List model """

    messages: list


class Date(BaseModel):
    """ Date model """

    start: str
    end: str
