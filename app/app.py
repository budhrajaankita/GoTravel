# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
#from worker import get_weather
import requests
import json
from datetime import datetime
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import openai

# Flask and postgre database configuration
app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/datawarehouse'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

OW_API_KEY = os.environ.get("OW_API_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
your_email= os.environ.get("your_email")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Database schema initialization
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(20), nullable=False)
    planned_date = db.Column(db.Date, nullable=False)
    weather_forecast = db.Column(db.String(200))
    recommendation = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'destination': self.destination,
            'planned_date': self.planned_date,
            'weather_forecast': self.weather_forecast,
            'recommendation': self.recommendation
        }


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


'''
/recommand - GET - ChatGPT API
- This endpoint will take in a JSON body with the key called "prompt"- {"prompt": "This is a prompt example"}
- This input would then be passed on to a queue and a worker task using the "delay" function in celery
- Return the status and corresponding response for that the task
'''


def get_recommend(destination):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[
            {"role": "user", "content": f"Recommend one place to go in {destination}, say the location name only"}
        ]
    )
    recommendation = completion.choices[0].message.content
    return recommendation

@app.route('/recommend/<destination>', methods=['GET'])
def recommend(destination):
    try:
        wishlist = Wishlist.query.filter_by(destination=destination).first()

        if wishlist:
            recommendation = get_recommend(destination)
            wishlist.recommendation = recommendation
            db.session.commit()
            return recommendation

        else:
            return jsonify("Error: Wishlist not found!"), 204
    except Exception as e:
        return jsonify(f"Error: Something went wrong when getting chatgpt recommendations - {str(e)}"), 400


'''
/wishlist - GET/POST/PUT/DELETE - OpenWeatherMap API
- This endpoint will handle the CRUD operations on wishlist
- Specifically, GET one particular destination in wishlist request will incorporate OpenWeatherMap API to provide local weather
'''


def handle_get_all():
    try:
        all_destinations = Wishlist.query.all()
        if all_destinations:
            return jsonify([destination.to_dict() for destination in all_destinations]), 200
        else:
            return jsonify("Error: Wishlist not found!"), 204
    except Exception as e:
        return jsonify(f"Error: Something went wrong when getting all wishlists - {str(e)}"), 400


def handle_create_wishlist():
    try:
        # Get user inputs from front-end form
        destination = request.form.get('destination')
        planned_date = request.form.get('planned_date')
        # Check the validity of user input
        if destination is None or destination == "" or planned_date is None or planned_date == "":
            return jsonify("Error: Invalid input"), 400
        # Strip any leading or trailing whitespaces in inputs and make them lowercase
        destination = destination.strip(" ").lower()
        planned_date = planned_date.strip(" ")

        # Check if the destination already exists in DB
        wishlist_db = Wishlist.query.filter_by(destination=destination).first()
        # If destination does NOT exist, add the user's desired destination and planned travel date into DB
        if not wishlist_db:
            new_wishlist = Wishlist(
                destination=destination, planned_date=planned_date)
            db.session.add(new_wishlist)
            db.session.commit()
            return jsonify("Success: New wishlist added!"), 201
        # If destination ALREADY exists, update the corresponding date to the destination into DB
        else:
            wishlist_db.planned_date = planned_date
            db.session.commit()
            return jsonify("Success: Wishlist updated!"), 201
    except Exception as e:
        return jsonify(f"Something went wrong when creating a new wishlist - {str(e)}"), 400


def handle_get_single(destination):
    try:
        wishlist = Wishlist.query.filter_by(
            destination=destination).first()
        # if wish_destination:
        #     return jsonify(wish_destination.to_dict()), 200
        if wishlist:
            planned_date = wishlist.planned_date
            task_res = get_weather(destination, planned_date)
            body = task_res.data.decode('utf-8')
            weather_forecast = str(body)
            wishlist.weather_forecast = weather_forecast
            db.session.commit()
            return jsonify(wishlist.to_dict()), 200
        else:
            return jsonify("Error: Wishlist not found!"), 204
    except Exception as e:
        return jsonify(f"Error: Something went wrong when getting a single wishlist - {str(e)}"), 400


def get_weather(destination, planned_date):
    try:
        # Convert the destination into exact geographical coordinates (latitude, longitude)
        resp_geo = requests.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={destination}&limit=1&appid={OW_API_KEY}")
        geo_data = resp_geo.json()
        lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

        # Get the weather information of the destination
        resp_weather = requests.get(
            f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OW_API_KEY}")
        weather_data = resp_weather.json()

        # Filter weather data based on the planned_date
        planned_date_format = datetime.strptime(str(planned_date), "%Y-%m-%d")
        #%H:%M:%S")
        relevant_forecast = None
        for forecast in weather_data['list']:
            forecast_date = datetime.strptime(str(forecast['dt_txt']), "%Y-%m-%d %H:%M:%S")
            if forecast_date == planned_date_format:
                relevant_forecast = forecast
                break

        if relevant_forecast:
            # convert to Celsius and only keep one decimal place
            temperature = round(relevant_forecast['main']['temp'] - 273.15, 1)
            weather = relevant_forecast['weather'][0]['description']
            return jsonify({"temperature": temperature, "weather": weather})
        return jsonify({"error": f"No forecast data found for {planned_date}. Only 5-day forecast available"})

        #    return json.dumps(f"Temperature: {temperature} '\u00b0'C, Weather: {weather}")
        #return json.dumps(f"Error: No forecast data found for {planned_date_format}. Only 5-day forecast available")
    except Exception as e:
        return f"Error: Something went wrong when getting weather details - {str(e)}"


def handle_update_single(destination):
    try:
        # Get user updated input from front-end form
        updated_date = request.form.get('planned_date')
        # Check the validity of user input
        if updated_date is None or updated_date == "":
            return jsonify("Error: Invalid input"), 400
        # Strip any leading or trailing whitespaces in input
        updated_date = updated_date.strip(" ")

        # Check if the destination already exists in DB
        wishlist_db = Wishlist.query.filter_by(destination=destination).first()
        # If destination ALREADY exists, update the corresponding date to the destination into DB
        if wishlist_db:
            wishlist_db.planned_date = updated_date
            db.session.commit()
            return jsonify("Success: Wishlist updated!"), 201
        # If destination does NOT exist, return error
        else:
            return jsonify("Error: Wishlist not found!"), 204
    except Exception as e:
        return jsonify(f"Error: Something went wrong when updating a single wishlist - {str(e)}"), 400

def handle_delete_single(destination):
    try:
        wishlist_item = Wishlist.query.filter_by(
            destination=destination).first()
        if wishlist_item:
            db.session.delete(wishlist_item)
            db.session.commit()
            return jsonify(f"Success: Destination '{destination}' removed from wishlist"), 201
        else:
            return jsonify(f"Error: Destination '{destination}' not found in wishlist"), 204
    except Exception as e:
        return jsonify(f"Error: Something went wrong when deleting the wishlist item - {str(e)}"), 400


@app.route('/wishlist/email', methods=['POST'])
def email_wishlist():
    try:
        recipient = request.form.get('email')
        wishlist = Wishlist.query.all()

        if not wishlist:
            return jsonify("Error: Wishlist is empty!"), 404

        wishlist_str = "\n".join([f"{w.destination} {w.planned_date} {w.weather_forecast} {w.recommendation}" for w in wishlist])

        message = Mail(
            from_email=your_email,
            to_emails=recipient,
            subject='Your Personal Wishlist',
            plain_text_content=wishlist_str
        )

        # Send the email using SendGrid API
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        return jsonify("Success: Wishlist emailed!"), 200
    except Exception as e:
        return jsonify(f"Error: Something went wrong when emailing wishlist - {str(e)}"), 400


@app.route('/wishlist', methods=['GET', 'POST'])
@app.route('/wishlist/<destination>', methods=['GET', 'PUT', 'DELETE'])
def wishlist(destination=None):
    try:
        if destination is None:
            if request.method == "GET":  # Get all wishlist
                return handle_get_all()
            elif request.method == "POST":  # Create a new wishlist
                return handle_create_wishlist()
            else:
                return jsonify("Error: Unsupported HTTP method"), 400
        else:
            if request.method == "GET":  # Get one single wishlist
                return handle_get_single(destination)
            elif request.method == "PUT":  # Update one single wishlist
                return handle_update_single(destination)
            elif request.method == "DELETE":  # Delete one single wishlist
                return handle_delete_single(destination)
            else:
                return jsonify("Error: Unsupported HTTP method"), 400
    except Exception as e:
        return jsonify(f"Error: Something went wrong in the wishlist endpoint - {str(e)}"), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
