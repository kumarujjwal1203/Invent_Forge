FROM python:3.9

WORKDIR /app

ENV INVENTEDGE_DATABASE_URL=file:inventedge.db

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN prisma db push

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
