# Movie recommendation project
#### Made by: ####

* Sumit Dey, cph-sd152@cphbusiness.dk
* Christoffer Ikizek Wegner, cph-cw109@cphbusiness.dk 

## INFO
The code editor used for this project is Visual Studio Code

Username and password for the different databases are located in settings.py

Make sure that the ports 27018,7687, 5432 & 6379 are unused, since they are used for the databases ins this project
## Usage

### Run the script *docker-compose-all.sh* to start all docker containers: ###

```bash
./docker-compose-all.sh
```

Run the following command in the root of the project to install requirements 

```bash
pip install -r requirements.txt
```

## Setup Neo4j

Run the following command to get the container id of the Neo4j docker container
```bash
docker ps
```

With the neo4j container id run the following commands to acces the neo4j container:

(On windows use winpty)

```bash
winpty docker exec -it <CONTAINER ID> bash
```

```bash
bin/cypher-shell
```

Enter the username: neo4j & password: password

Run following cypher. This step will take about 5-6 minutes since the csv file contains 30.000 rows

Meanwhile finish the rest of the README.md file

```bash
USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM "file:///movies.csv" AS line  
MERGE (m:Movie{ id:line.movieId, title:line.title})   
FOREACH (gName in split(line.genres, '|') | MERGE (g:Genre {name:gName}) MERGE (m)-[:IS_GENRE]->(g));
```

## Setup Postgres

Run the following command in a new terminal to get the container id of the postgres docker container
```bash
docker ps
```

With the postgres container id run the following commands to acces the postgress container:

(On windows use winpty)

```bash
winpty docker exec -it <CONTAINER ID> bash
```

Run the following command
```bash
psql -h localhost -U postgres
```
Copy the content of [sql](https://github.com/dofinator/db_eksamen_22/blob/master/create_tables.sql) to your clipboard and paste it in the postgres-cli and press enter


### Test users
| Email     | Password | Role |
| ----------- | ----------- | ----------- 
| admin@admin.com      | 1234       | admin |
| user@user.com   | 1234       | user |


## Start the API's
Run the following script from the root of the project:

```bash
./start_servers.sh
```

If the above bash script did not work, open the bash script with an editor and run each of the 3 start commands in 3 seperatly terminals

:warning: **Check to see if the neo4j cypher has finished running before accessing the client**


## Acces client at http://localhost:5000/
