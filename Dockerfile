FROM python:3.10

WORKDIR /usr/src/
ADD requirements.txt .


RUN apt-get install curl
RUN apt-get install apt-transport-https
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list | tee /etc/apt/sources.list.d/msprod.list
RUN apt-get remove unixodbc mssql-tools odbcinst libodbc1
RUN apt-get update
RUN apt-get install mssql-tools unixodbc-dev

RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN source ~/.bashrc

COPY . .

RUN pip install --upgrade pip

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]