FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Keep system packages minimal for hosted-embeddings path to speed up builds
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		git \
	&& rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
