# Movie recommendation project
Database Exam Project
Christoffer Wegner
Sumit Dey

## Usage
Run the following command to activate the virtual environment where the requirements are installed.
```bash
source venv/Scripts/activate
```

## Setup Postgres
Run the following [sql](https://github.com/dofinator/db_eksamen_2022/blob/master/create_tables.sql) file in your local postgres to setup some test users.
### Test users
| Email     | Password |
| ----------- | ----------- |
| test@test.dk      | test       |
| test2@test.dk   | test2        |

## Setup MongoDB

## Setup Neo4j
To run Neo4j locally setup these variables in reviews.py and neo.py to let the application know where to connect to the database.
```bash
NEO4J_URI=neo4j://localhost:7687 NEO4J_DATABASE=neo4j NEO4J_USER="<username>" NEO4J_PASSWORD="<password>" python movies.py
```

## Setup Redis
