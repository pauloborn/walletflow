For Windows use the Docker below
https://dev.to/jfhbrook/how-to-run-airflow-on-windows-with-docker-2d01

Run with PowerShell
.\Invoke-Airflow.ps1 db init

mkdir data

TODO: Script to create folders and files for basic development
TODO: Implantar Bandit
TODO: pytest-benchmark

docker-compose run airflow-webserver airflow users create --role Admin --username airflow --email airflow --firstname airflow --lastname airflow --password airflow
