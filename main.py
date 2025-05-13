from flask import Flask, redirect, request, render_template
from database import cities

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

@app.route('/get-city-desc', methods=['POST'])
def get_city_desc():
    city = request.form.get("city")
    desc = "No Option Selected"
    for c in cities:
        if(c.name.lower() == city.lower()):
            desc = c.description
            break
    return desc


@app.route('/get-city-locations', methods=['POST'])
def get_location_info():
    city = request.form.get("city")
    for c in cities:
        if(c.name.lower() == city.lower()):
            return render_template("location-sub-template.html", locations = c.locations)
    return redirect("error", 404)

@app.route('/error')
def error():
    return render_template("error.html")

# TRP Service :-
@app.route('/trp-service')
def trp_service():
    cities_names = [c.name for c in cities]
    return render_template("trp-service.html", cities = cities_names)



if __name__ == '__main__':
    app.run(debug=True)