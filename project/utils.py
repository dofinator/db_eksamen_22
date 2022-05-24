import psycopg2 


def get_connection_postgres(CONNECTION):
        return psycopg2.connect(CONNECTION)