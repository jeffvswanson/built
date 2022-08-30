Proof of concept Built Budget API - **DO NOT USE IN PRODUCTION!**

# Requirements
## Core Technologies:

- Docker
- Flask
- Python >=3.7
- SqlAlchemy + Alembic
- Marshmallow
- Pipenv
- PyTest

## Acceptance Criteria:

1. Create a restful API using Built Core Technologies
	- CRUD endpoint for a “Budget Item” using SQLAlchemy (improvise on the fields, but want to see some critical thinking)
	  - built/budgeter/budget.py
      - built/budgeter/payee.py
	- example leveraging marshmallow schema for validation & serialization
	  - built/budgeter/schemas
	- example query / migration using SQLAlchemy
	  - built/budgeter/budget.py
      - built/budgeter/payee.py
	  - built/budgeter/alembic/
	- Testing
	  - built/tests

2. Create a docker-compose to orchestrate the following
	- Flask API from Step 1
	- [localstack/localstack](https://github.com/localstack/localstack)
	- MySql >= 5.7 [Docker](https://hub.docker.com/_/mysql)
	- Sample Postman collection to your API (you can include the collection.json in Github) 
      - https://www.postman.com/
	- Demonstrate connectivity between your docker network and localstack using Kinesis  
      - (https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html)

# Runbook
## Installation

1. Clone the Built API git repository from https://github.com/jeffvswanson/built
2. Assuming python 3.9 is installed.
3. From the `./built` directory
4. Run `pipenv sync`
5. Check installation with `pipenv run python -m pytest ./tests/`

## Stand Up System

1. From the `./built` directory
2. Run `docker compose up --build`
3. Watch the services stand up.
4. If the system is being stood up for the first time or the local volume mount for the MySQL database was destroyed and rebuilt, perform an Alembic migration to populate the database with the table definitions with:  
    ```shell
    pipenv run alembic upgrade head
    ```

## Monitoring

`adminer` allows investigation of the MySQL database running in the docker compose network.  
The `adminer` interface can be accessed from a browser at http://localhost:8080 with appropriate credentials.

## Tear Down System

1. From the `./built` directory
2. Run `docker compose down` or `docker compose down --volumes` to get rid of the database local file storage volume.

# Improvements
## Performance
- Study use of async functions when making network calls to the database/localstack
## API
### Get All
- Could use a limit/paginator
### Create
- Consider a batch creator
### Delete
- Consider a batch delete
### Update
- Consider a batch update

## Testing
- Add a more robust set of unit tests, e.g., utilize property based testing with hypothesis.
- Higher test coverage for more edge cases/error conditions.
- Create a functional test environment to run commands against an existing database backend.
