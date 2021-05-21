#Dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#Database Setup and reflect database and tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

Base = automap_base()
Base.prepare(engine, reflect=True)

#References to the Table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#Flask 
app = Flask(__name__)

#Routes
@app.route("/")
def welcome():
    """List all available routes"""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of last years precipitation from all stations.<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Stations.<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of temperatures from last year of all stations.<br/>"
        f"<br/>"
        f"/api/v1.0/start/<br/>"
        f"- The minimum temperature, the average temperature, and the max temperature for all dates greater than and equal to the start date.<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- The minimum temperature, the average temperature, and the max temperature for dates between the start and end date inclusive.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return Precipitation for the Last Year"""
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    last_year = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    precipitation_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()



    precipitation_lists = dict(precipitation_scores)

    return jsonify(precipitation_lists)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    stations_result = session.query(Measurement.station).group_by(Measurement.station).all()
    list_stations = list(np.ravel(stations_result))

    return jsonify(list_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = recent_date[0]
    last_year = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    temperature_observations = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year).all()

    
    temperature_lists = list(temperature_observations)

    return jsonify(temperature_lists)

@app.route("/api/v1.0/<start>/")
def start(start=None):

    start_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_date_list = list(start_date)
    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    
    start_end_date = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    start_end_date_list = list(start_end_date)
    return jsonify(start_end_date_list)


if __name__ == '__main__':
    app.run(debug=True)

    