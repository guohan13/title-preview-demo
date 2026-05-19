FROM python:3.11-slim

WORKDIR /app

COPY . /app

ENV PREVIEW_HOST=0.0.0.0
ENV PREVIEW_PORT=8000

EXPOSE 8000

CMD ["python3", "sync_server.py"]
