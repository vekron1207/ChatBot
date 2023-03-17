from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

# database connection details
db_host = "your_host"
db_name = "your_db_name"
db_user = "your_db_username"
db_password = "your_db_password"

# database connection
conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)


@app.route('/')
def index():
    # Retrieve the user statistics
    cur = conn.cursor()
    cur.execute(
        'SELECT user_id, stupid_calls, fat_calls, dumb_calls FROM user_stats')
    rows = cur.fetchall()
    cur.close()

    return render_template('index.html', rows=rows)


if __name__ == '__main__':
    app.run()
