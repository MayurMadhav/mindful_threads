import mysql.connector

# Create connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="test"
)

# Check if connection is successful
if connection.is_connected():
    print("Connected to MySQL Server")

# Register function
def register(username, password, email, fun):
    cursor = connection.cursor()
    insert_query = "INSERT INTO user (username, password, email) VALUES (%s, %s, %s)"
    insert_data = (username, password, email)
    try:
        cursor.execute(insert_query, insert_data)
        connection.commit()
        fun(True)
    except mysql.connector.Error as err:
        print("Error:", err)
        fun(False)
    finally:
        cursor.close()

# Login function
def login(username, password, fun):
    cursor = connection.cursor()
    select_query = "SELECT * FROM user WHERE username = %s AND password = %s"
    select_data = (username, password)
    try:
        cursor.execute(select_query, select_data)
        result = cursor.fetchall()
        if len(result) > 0:
            fun(True)
        else:
            fun(False)
    except mysql.connector.Error as err:
        print("Error:", err)
        fun(False)
    finally:
        cursor.close()

# Insert post function
def insert_post(username, comment, sentiment):
    cursor = connection.cursor()
    select_query = "SELECT id FROM user WHERE username = %s"
    select_data = (username,)
    cursor.execute(select_query, select_data)
    result = cursor.fetchone()
    if result:
        authorid = result[0]
        insert_query = "INSERT INTO post (authorid, post, sentiment) VALUES (%s, %s, %s)"
        insert_data = (authorid, comment, sentiment)
        try:
            cursor.execute(insert_query, insert_data)
            connection.commit()
            print("Post inserted successfully.")
        except mysql.connector.Error as err:
            print("Error:", err)
        finally:
            cursor.close()
    else:
        print("User not found.")

# Get post function
def get_post(fun):
    cursor = connection.cursor(dictionary=True)
    select_query = "SELECT post.authorid, post.post, post.posted_at, user.username FROM post JOIN user ON post.authorid = user.id"
    try:
        cursor.execute(select_query)
        result = cursor.fetchall()
        fun(result)
    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        cursor.close()

# Get last five data function
def get_last_five_data(fun):
    cursor = connection.cursor(dictionary=True)
    query = "SELECT authorid, SUM(CASE WHEN sentiment = 'suicide' THEN 1 ELSE 0 END) AS suicide_count, SUM(CASE WHEN sentiment IS NULL OR sentiment != 'suicide' THEN 1 ELSE 0 END) AS non_suicide_count FROM post WHERE posted_at >= NOW() - INTERVAL 5 DAY GROUP BY authorid"
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        fun(result)
    except mysql.connector.Error as err:
        print("Error:", err)
    finally:
        cursor.close()

# Close connection
def close_connection():
    if connection.is_connected():
        connection.close()
        print("Connection closed.")

# # Usage example
if __name__ == "__main__":

    get_post(print)
    close_connection()
