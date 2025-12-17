FROM python:3.11-slim

WORKDIR /app

# copy requirements จาก subfolder
COPY coupon-bot/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# copy โค้ดทั้งหมด
COPY coupon-bot/ .

CMD ["python", "bot.py"]
