import uvicorn

if __name__ == '__main__':
    # Run the server
    uvicorn.run('fastapi_redis.app:app', host='0.0.0.0', port=9000)
