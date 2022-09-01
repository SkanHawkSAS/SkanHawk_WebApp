FROM python:3.10

WORKDIR /usr/src/
ADD requirements.txt .


RUN if ! [[ "16.04 18.04 20.04 22.04" == *"$(lsb_release -rs)"* ]]; \
then\
    echo "Ubuntu $(lsb_release -rs) is not currently supported.";\
    exit;\
fi\
sudo su\
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -\
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list\
exit\
sudo apt-get update\
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17\
# optional: for bcp and sqlcmd
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools\
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc\
source ~/.bashrc\
# optional: for unixODBC development headers
sudo apt-get install -y unixodbc-dev


COPY . .

RUN pip install --upgrade pip

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]