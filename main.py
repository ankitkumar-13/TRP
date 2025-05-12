from flask import Flask, redirect, render_template

# Application Instance : Flask Object
app = Flask(__name__)


# Homepage
@app.route('/')
def home():
    return render_template("index.html")

# Contact Us
@app.route('/contact-us')
def contact_us():
    return render_template("contact-us.html")

# TRP Service :-
@app.route('/trp-service')
def trp_service():
    cities = ["Dehradun", "Agra", "Delhi"]
    return render_template("trp-service.html", cities = cities)



if __name__ == '__main__':
    app.run(debug=True)