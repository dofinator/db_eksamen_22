import psycopg2 
from werkzeug.security import generate_password_hash, check_password_hash

def get_connection_postgres(CONNECTION):
        return psycopg2.connect(CONNECTION)



