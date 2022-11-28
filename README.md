For Windows use the Docker below
https://dev.to/jfhbrook/how-to-run-airflow-on-windows-with-docker-2d01

.\Invoke-Airflow.ps1 db init

mkdir data

TODO: Script to create folders and files for basic development
TODO: Implantar Bandit
TODO: pytest-benchmark

docker-compose run webserver airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
