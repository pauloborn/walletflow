# Airflow finance flow

## Description
This project aims to automatize the flow to capture data from different type of bank accounts and merge togheter all expenses on the same table.
Currently it's working only with Nubank, but in the future it'll have others banks too.

A Dag called Finance with 3 task (crawler, normalize and contextualize) is responsible to manage the flow. The crawler capture the data and store on a local file.
When nomalize runs, it merge all the data and apply some filters and categorizations.
To finish, the contextualize run and send it to a postgres database, which have only one table set.
I'm using a supert to visualize all the data.

---

## Setup
To setup this project with docker there are three steps, unfortunetly I'm coding in a Windows environment and I have to execute some additionals steps.

### Pre-requirements
1. Docker
2. The following folders/files should be created or exists: `.data`, `.airflow/airflow.cfg`
3. The certification to connect with Nubank, you can learn how to create it here: [Pynubank](https://github.com/andreroggeri/pynubank)
After creating the .p12 file you must include in the `.secrets` folder.
4. A file named .secret/secrets.json with your bank configuration (for obvious reason you cannot publish it)

### Configuration
1. Run the following command to build a custom airflow image \
`docker-compose build`

2. After building it, everything should had work like a charm, you can start the conatiners
`docker-compose up`

3. After this there are some steps that I still didn't figure out how to not need to execute it. There is no need to wait until all the steps below. It's important to notice that your airflow webserver will still keeping to died until you execute the first step.
In a power shell window execute `./Invoke-Airflow.ps1 db init`

4. Create airflow user
`docker-compose run airflow-webserver airflow users create --role Admin --username airflow --email airflow --firstname airflow --lastname airflow --password airflow`

For more information about this steps you can check this link:
[Airflow on Windows Docker](https://dev.to/jfhbrook/how-to-run-airflow-on-windows-with-docker-2d01)


---
I hope, you can use or be inspire by this project. 

---
Maybe furture TODO's

TODO: Implantar Bandit
TODO: pytest-benchmark

