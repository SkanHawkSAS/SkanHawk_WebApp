FROM python:3.10

WORKDIR /usr/src/
ADD requirements.txt .

COPY . .

RUN pip install --upgrade pip

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "20.245.97.178/", "--port", "8000"]