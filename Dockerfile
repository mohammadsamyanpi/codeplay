FROM python:3.13-slim
WORKDIR /app
RUN useradd --create-home codeplay && mkdir /app/data && chown codeplay:codeplay /app/data
COPY server.py catalog.py app.js learning.js index.html styles.css python-worker.js ./
COPY assets ./assets
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CODEPLAY_DB=/app/data/codeplay.sqlite3
USER codeplay
EXPOSE 8000
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
