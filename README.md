FastAPI-Redis
=================

## Installation

### Docker

Download and install Docker Desktop for Windows:

```
https://www.docker.com/get-started
```

If docker does not start, download the Linux kernel update package (Docker uses the Linux kernel):

```
https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
```

Then set WSL 2 as your default version:

```
wsl --set-default-version 2
```

## Run

Build, (re)create, start, and attach to containers for a service. Both Redis and FastAPI will run on separate
containers.

```
$ docker-compose up -d
```

To list the running containers:

```
$ docker container ls
```

To stop the running containers:

```
$ docker stop [CONTAINER ID]
```

## Run tests:

```
$ docker-compose up -d
$ docker-compose run --rm messages_api pytest
```

## Solution to Store Messages in Redis:

A sorted set is used to store all messages. The key is the name of the set, the score is the timestamp, and the value is
the message with a UUID appended at the end to ensure the uniqueness of the message.

Example publish new message:

```
zadd messages 1624438855 "message.073f0283-71bc-420f-bd98-c2a204da3589"
```

Example get last message:

```
zrevrangebyscore messages +inf -inf LIMIT 0 1
```

Example get messages between dates:

```
zrangebyscore messages 1624438854 1624438856
```

## Endpoints:

### POST http://localhost:9000/api/publish:

request body:

```
{
   "content":"message"
}
```

response body:

```
{
   "success":"new message added"
}
```

### GET http://localhost:9000/api/getlast:

request body:

```
None
```

response body:

```
{
   "content":"message"
}
```

### GET http://localhost:9000/api/getbytime:

request body:

```
{
   "start":"2021-06-23T09:00:00",
   "end":"2021-06-23T17:00:00"
}
```

response body:

```
{
   "messages":[
      {
         "content":"message 1"
      },
      {
         "content":"message 2"
      },
      {
         "content":"message 3"
      }
   ]
}
```
