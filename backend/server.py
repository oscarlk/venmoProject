from flask import Flask
from read_emails import get_venmo_data
app = Flask(__name__)

@app.route('/getVenmoData')
def get_venmo_data_route():
    obj = get_venmo_data()
    return obj

@app.route('/')
def home():
    return "Home page."


if __name__ == '__main__':
    app.run(port=8000, debug=True)