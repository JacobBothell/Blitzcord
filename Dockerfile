FROM python:3.10.30-slim

RUN apt-get update && apt-get install wget git

RUN git clone https://github.com/JacobBothell/Blitzcord.git /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]