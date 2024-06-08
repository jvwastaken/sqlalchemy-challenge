# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
import numpy as np


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify, request

app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    past12_months_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= '2016-08-23').\
        order_by(measurement.date).all()
    
    session.close()
    list_to_append = []

    for date, prcp in past12_months_data:
        dict = {}
        dict['date'] = date
        dict['precipitation'] = prcp
        list_to_append.append(dict)

    return jsonify(list_to_append)


@app.route("/api/v1.0/stations")
def stations():
    station = Base.classes.station
    all_stations = session.query(station.station, station.name).all()
    
    session.close()
    list_of_stations = []

    for station, name in all_stations:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        list_of_stations.append(station_dict)

    return jsonify(list_of_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    measurement = Base.classes.measurement
    mostactive_12months = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
            filter(measurement.date >= '2016-08-18').all()
    
    session.close()

    list_of_date = []

    for date, tobs in mostactive_12months:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['Observed Temp'] = tobs
        list_of_date.append(tobs_dict)

    return jsonify (list_of_date)

''' XPert Learning Assistant was used to aid me in generating and correcting all code for <start> and <start>/<end> routes'''

@app.route("/api/v1.0/<start>")
def start_route(start):
    measurement = Base.classes.measurement
    # Convert the start date string to a datetime object
    start_date = datetime.strptime(start, '%Y-%m-%d')

    # Query to get min, max, and avg temperatures from the start date to the end of the dataset
    results = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

    session.close()

 # Create a list of dictionaries to store temperature data for each date
    temp_data_list = []
    for result in results:
        temp_data = {
            "start date": result.date,
            "min_temp": results[0][0],
            "max_temp": results[0][1],
            "avg_temp": results[0][2]
        }
        temp_data_list.append(temp_data)

    # Return the temperature data list as JSON
    return jsonify(temp_data_list)


@app.route('/api/v1.0/<start>/<end>')
def start_and_end(start, end):

    # Convert the start and end date strings to datetime objects
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    # Query to get temperature data for each date between the start and end dates
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start_date, measurement.date <= end_date).all()

    # Query to calculate min, max, and average temperatures for the specified date range
    temp_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date, measurement.date <= end_date).all()
    
    session.close()

    # Extracting the temperature statistics
    min_temp, max_temp, avg_temp = temp_stats[0]

    # Creating a dictionary with the temperature statistics
    temperature_data = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'min_temp': min_temp,
        'max_temp': max_temp,
        'avg_temp': avg_temp
    }

    # Return the temperature data list as JSON
    return jsonify(temperature_data)

if __name__ == "__main__":
    app.run(debug=True)