FROM python

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /photo_share

COPY . /photo_share

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
