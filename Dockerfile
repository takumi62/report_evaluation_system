FROM python:3.11.0-buster

WORKDIR /workdir

COPY requirements.txt /workdir

ENV LANG ja_JP.UTF-8

# タイムゾーン設定
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo
RUN apt-get update && apt-get install -y --no-install-recommends tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r /workdir/requirements.txt 

# アプリケーションコードをコピー
COPY . .

# 実行コマンド
CMD ["python", "app/main.py"]
