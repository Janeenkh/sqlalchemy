import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database 
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references
measurement = Base.classes.measurement
stations = Base.classes.station



# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home(): 
    routes = (
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br>")
    return routes
    


# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query dates and precipitation
    session = Session(engine)
    last_date_str = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

     #Calculate the date one year from the last date in data set.
    last_date = dt.datetime.strptime(last_date_str, '%Y-%m-%d').date()
    
    year_from= last_date - dt.timedelta(days=365)
   
    year_data = session.query(measurement.date, measurement.prcp)\
        .filter(measurement.date >= year_from)\
        .filter(measurement.date <= last_date)\
        .all()

    prcp_dict = {}
    #prcp_list = []
    for obs in year_data:
        date = obs[0]
        prcp = obs[1] 
        prcp_dict[date] = prcp
        #prcp_list.append(prcp_dict) 
        print(obs)
    session.close()

    # # Json representation
    return jsonify(prcp_dict)
    


# Total stations
@app.route("/api/v1.0/stations")
def stations():
    
    # Station list
    session = Session(engine)
    station_list = session.query(measurement.station).distinct().all()
    stations_list = list(np.ravel(station_list))
    # Json List of station
    return jsonify(stations_list)



# Temperature observation
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Most active station previous year data
    session = Session(engine)
    last_date = session.query(measurement.date).all()
    last_date = last_date[-1][0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    last_date = last_date.date()
    one_year_date = last_date - dt.timedelta(days=365)
    
    #Temperature observation for previous year
    prev_year= session.query(measurement.date, measurement.tobs).\
	    filter(measurement.date > one_year_date).all()

    
    
    
    # Creating list of previous year data
    tobs_list = []

    for date, tobs in prev_year:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict) 

    session.close()

    # Json temp observation for previous year
    return jsonify(tobs_list)



# Given start date route min, max, avg
@app.route('/api/v1.0/<start>')
def start(start):
    
    # Query dates and temperature observations
    session = Session(engine)
    date_start = session.query(func.min(measurement.date)).first()[0]
    date_end = session.query(func.max(measurement.date)).first()[0]
   
    if start >= date_start and start <= date_end:
        calc_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= date_end).all()[0]
    
        return (
            f"Min temp: {calc_temps[0]}</br>"
            f"Avg temp: {calc_temps[1]}</br>"
            f"Max temp: {calc_temps[2]}")
    else:
        return jsonify()

# # Given start and end date route min, max, avg
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
# Query dates and temperature observations
    session = Session(engine)

# Select first and last dates 
    date_start = session.query(func.min(measurement.date)).first()[0]
    date_end = session.query(func.max(measurement.date)).first()[0]

# Calculate temperatures 
    if start >= date_start and end <= date_end:
        calc_temps = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= end).all()[0]
    
        return (
            f"Min temp: {calc_temps[0]}</br>"
            f"Avg temp: {calc_temps[1]}</br>"
            f"Max temp: {calc_temps[2]}")
    
    else:
        return jsonify()

if __name__=="__main__":
    app.run()