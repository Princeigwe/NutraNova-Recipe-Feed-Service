from django.db import connection, connections

# this function is called in settings.py
# this table is designed to keep track of the total amount of messages sent to the stream, 
# which will act as the offset when consuming messages that were missed as a result of downtime and network failure
def create_offset_table():
  try:
    # Check if the default database connection is alive
    connections['default'].cursor()
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS rabbitmq_message_offset ( id INT PRIMARY KEY NOT NULL, message_offset INT NOT NULL)")
    print("table created")
  except Exception:
    return None


def create_offset_record(id, offset):
  cursor = connection.cursor()
  # check if the record with the given ID already exists
  cursor.execute(
    """
    SELECT 1 FROM rabbitmq_message_offset WHERE id = %s
    """, [id])
  existing_record = cursor.fetchone()

  if not existing_record:
    cursor.execute(
      """
      INSERT INTO rabbitmq_message_offset (id, message_offset)
      VALUES (%s, %s)
      """, [id, offset]
    )
    print(f"Record with ID {id} and message_offset {offset} created.")


def update_offset_record(id, new_offset):
  cursor = connection.cursor()
  cursor.execute(
    """
    UPDATE rabbitmq_message_offset
    SET message_offset = %s
    WHERE id = %s
    """, [new_offset, id]
  )


def get_offset_record(id):
  cursor = connection.cursor()
  cursor.execute(
    """
    SELECT id, message_offset
    FROM rabbitmq_message_offset
    WHERE id = %s
    """, [id]
    )
  row = cursor.fetchone()
  if row:
    return row