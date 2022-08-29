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

## Stand Up System

## Tear Down System


# Improvements
## API
### Get All
- Could use a limit/paginator
### Create
- Consider a batch creator
### Delete
- Consider a batch delete
### Update
- Consider a batch update
