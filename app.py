from flask import Flask
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "Soccer Dashboard is running!"

@app.route('/time')
def current_time():
    now = datetime.datetime.now()
    return f"Current server time is: {now.strftime('%Y-%m-%d %H:%M:%S')}"

if __name__ == '__main__':
    app.run(debug=True)
