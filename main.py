if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)

# gunicorn src.app:app -k uvicorn.workers.UvicornWorker -w 6 -b 0.0.0.0:8000 --timeout 600 --keep-alive 120
