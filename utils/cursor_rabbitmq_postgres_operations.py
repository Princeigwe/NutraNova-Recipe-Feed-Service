import psycopg2
import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", default="production" )

db_params = {
  'dbname': os.environ.get('AIVEN_DATABASE_NAME') if ENVIRONMENT == 'production' else os.environ.get('DEV_RECIPES_DB_NAME'),
  'user': os.environ.get('AIVEN_USER') if ENVIRONMENT == 'production' else os.environ.get('DEV_RECIPES_DB_USERNAME'),
  'password': os.environ.get('AIVEN_PASSWORD') if ENVIRONMENT == 'production' else os.environ.get('DEV_RECIPES_DB_PASSWORD'),
  'host': os.environ.get('AIVEN_HOST') if ENVIRONMENT == 'production' else os.environ.get('DEV_RECIPES_DB_HOST'),
  'port': os.environ.get('AIVEN_PORT') if ENVIRONMENT == 'production' else os.environ.get('DEV_RECIPES_DB_PORT')
}

def create_custom_rabbitmq_user_message_id_table():
  create_table_query = """
  CREATE TABLE IF NOT EXISTS custom_rabbitmq_user_message_id (
    id SERIAL PRIMARY KEY,
    rabbitmq_message_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )
  """
  try:
    print("Creating rabbitmq user message id table...")
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    connection.commit()
    print("Table created successfully")
  except (Exception, psycopg2.DatabaseError) as error:
    print("Error: ", error)
  finally:
    if cursor:
      cursor.close()
    if connection:
      connection.close()


def get_custom_rabbitmq_user_message_ids():
  select_query = """
  SELECT rabbitmq_message_id FROM custom_rabbitmq_user_message_id
  """
  try:
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(select_query)
    user_message_ids_records = cursor.fetchall()
    print("User message ids: ", user_message_ids_records)
    user_message_ids = [record[0] for record in user_message_ids_records] # creating a list of user message ids
    return user_message_ids
  except (Exception, psycopg2.DatabaseError) as error:
    print("Error: ", error)
  finally:
    if cursor:
      cursor.close()
    if connection:
      connection.close()


def update_custom_rabbitmq_user_message_ids(rabbitmq_message_id, created_at):
  insert_query = """
  INSERT INTO custom_rabbitmq_user_message_id (rabbitmq_message_id, created_at) VALUES (%s, %s)
  """
  try:
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    cursor.execute(insert_query, (rabbitmq_message_id, created_at))
    connection.commit()
    print("Message id inserted successfully")
  except (Exception, psycopg2.DatabaseError) as error:
    print("Error: ", error)
  finally:
    if cursor:
      cursor.close()
    if connection:
      connection.close()