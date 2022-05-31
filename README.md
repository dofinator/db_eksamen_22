# Movie recommendation project
#### Made by: ####

* Sumit Dey, cph-sd152@cphbusiness.dk
* Christoffer Ikizek Wegner, cph-cw109@cphbusiness.dk 

## INFO
The code editor used for this project is Visual Studio Code

Username and password for the different databases are located in settings.py

## Usage

**Run the script *docker-compose-all.sh* to start all docker containers:**

```bash
./docker-compose-all.sh
```


**Run the following command to activate the virtual environment where the requirements are installed: Use the git bash terminal to execute the command in the terminal in Visual Studio Code**
```bash
source venv/Scripts/activate
```
## Setup Neo4j
Run the following query in your local Neo4j desktop application: 

This step will take about 5-6 minutes since the csv file contains 30.000 rows

`:auto USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///movies.csv" AS line  
MERGE (m:Movie{ id:line.movieId, title:line.title})   
FOREACH (gName in split(line.genres, '|') | MERGE (g:Genre {name:gName}) MERGE (m)-[:IS_GENRE]->(g) )`

## Setup Postgres
Run the following [sql](https://github.com/dofinator/db_eksamen_2022/blob/master/create_tables.sql) file in your local postgres, to setup some test users.
### Test users
| Email     | Password | Role |
| ----------- | ----------- | ----------- 
| admin@admin.dk      | 1234       | admin |
| user@user.dk   | 1234       | user |


## Start the API's
Run the following commands in the terminal from the project folder:

```bash
python gateway.py
```

```bash
python microservice_mongo.py
```

```bash
python microservice_neo.py
```
## Acces client at http://localhost:5000/
