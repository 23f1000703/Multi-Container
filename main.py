from fastapi import FastAPI, HTTPException
import redis
import os

app = FastAPI()

redis_client = None


@app.on_event("startup")
def startup():
    global redis_client

    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        decode_responses=True,
    )

    # Verify Redis connection
    redis_client.ping()


@app.post("/hit/{key}")
def hit(key: str):
    try:
        count = redis_client.incr(key)
        return {
            "key": key,
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/count/{key}")
def count(key: str):
    try:
        value = redis_client.get(key)
        return {
            "key": key,
            "count": int(value) if value else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/healthz")
def healthz():
    try:
        redis_client.ping()
        return {
            "status": "ok",
            "redis": "up"
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "redis": "down"
            }
        )