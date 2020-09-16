FROM python:3.8.5
COPY ./SF_E7.11_back/requirements.txt /app/requirements.txt
COPY ./SF_E7.11_back/app/main.py /app/main.py
COPY ./SF_E7.11_back/app/models.py /app/models.py
COPY ./SF_E7.11_back/app/utils/db.py /app/utils/db.py
COPY ./SF_E7.11_back/app/utils/typecodecs.py  /app/utils/typecodecs.py
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
