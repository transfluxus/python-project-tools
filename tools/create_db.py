import sqlalchemy

from sqlalchemy_utils import database_exists, create_database

from config import PG_CONFIG


def connection_str(db_name: str= "postgres") -> str:
    admin = PG_CONFIG.PG_ADMIN_NAME
    host = PG_CONFIG.PG_HOSTNAME
    port = PG_CONFIG.PG_PORT
    pwd = PG_CONFIG.PG_ADMIN_PASSWORD.get_secret_value()
    return f"postgresql+psycopg2://{admin}:{pwd}@{host}:{port}/{db_name}"

def create_pg_db(db_name: str):

    #default_connection_string = f"postgresql+psycopg2://postgres:{pwd}@localhost/postgres"

    # Define the connection string for the database we want to create
    new_db_connection_string = connection_str(db_name)

    # Create the new database
    if not database_exists(new_db_connection_string):
        create_database(new_db_connection_string)
        print(f"Database '{db_name}' created successfully.")
    else:
        print(f"Database '{db_name}' already exists.")

    # Connect to the new database
    new_engine = sqlalchemy.create_engine(new_db_connection_string)

    # Test the connection
    with new_engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1"))
        print(f"Connected to '{db_name}' successfully.")

def get_engine(username: str, password: str, db_name: str) -> sqlalchemy.Engine:
    return sqlalchemy.create_engine(f"postgresql+psycopg2://{username}:{password}@localhost/{db_name}")

def create_user_grant_access(username: str, password: str, database_name: str):
    # SQL commands
    sql_commands = f"""
    CREATE USER {username} WITH PASSWORD '{password}';
    GRANT CONNECT ON DATABASE {database_name} TO {username};
    GRANT USAGE ON SCHEMA public TO {username};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {username};
    ALTER DATABASE {database_name} OWNER TO {username};
    GRANT CREATE ON SCHEMA public TO {username};
    """

    pwd = PG_CONFIG.PG_PASSWORD.get_secret_value()
    # Execute the SQL commands
    with get_engine("postgres", pwd,"postgres").connect() as conn:

        conn.execute(sqlalchemy.text(f"DROP USER IF EXISTS {username}"))

        conn.execute(sqlalchemy.text("COMMIT"))  # Ensure we're not in a transaction
        for command in sql_commands.split(';'):
            if command.strip():
                conn.execute(sqlalchemy.text(command))
        conn.execute(sqlalchemy.text("COMMIT"))

    print("User created and permissions granted successfully.")


if __name__ == "__main__":

    # new_engine = sqlalchemy.create_engine(connection_str())
    # connection = new_engine.connect()

    create_pg_db("twitter_index")
    #create_user_grant_access("labelstudio_admin","asas","labelstudio")