from flask import Flask
app = Flask(__name__)

@app.route('/getAverageTime')
def get_average_time():
    return {"average_time": "Hello World"}

@app.route('/')
def home():
    return "Home page."


if __name__ == '__main__':
    app.run(port=8000, debug=True)