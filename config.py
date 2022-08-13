import mariadb
# Enter your channel id and your API key
channel_id = 'UCFbRInXctfkG3o9gcVd2qog'
API_KEY = "you api key"

# MariaDB credentials

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Kashif0047@',
    'database': 'flask-test'
}
conn = mariadb.connect(**config)
cur = conn.cursor()
