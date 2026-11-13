
from sqlalchemy import text
from connection import get_engine


def test_connection():
    engine = get_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), current_user, version();")
            )

            database, user, version = result.fetchone()

            print("Connection successful!")
            print(f"Database: {database}")
            print(f"User: {user}")
            print(f"PostgreSQL: {version.split(',')[0]}")

    except Exception as error:
        print("Connection failed!")
        print(error)

    finally:
        engine.dispose()


if __name__ == "__main__":
    test_connection()
