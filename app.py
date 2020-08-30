import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect Database into ORM classes
Base = automap_base()
Base.prepare(engine, reflect=True)
hawaii = Base.classes.keys()

# Create a database session object
# session = Session(engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Creating a variable
after_start_date = (measurement.date >= (dt.date(2016,8,23)))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# All available routes
@app.route("/")
def welcome():
    """All available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        )

# Return a JSON representation of a dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precip_results = session.query(measurement.date, measurement.prcp).all()
    session.close()
    
    precip_dictionary = list(np.ravel(precip_results))
    return jsonify(precip_dictionary)

# Return a JSON list of stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_results = session.query(station.station, station.name).all()
    session.close()
    
    station_dictionary = list(np.ravel(station_results))
    return jsonify(station_dictionary)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs_results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date.between(dt.date(2016,8,23),\
            dt.date(2017,8,23))).all()
    session.close()
    
    tobs_dictionary = list(np.ravel(tobs_results))
    return jsonify(tobs_dictionary)

# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
def start():
    session = Session(engine)
    start_results = session.query(func.min(measurement.tobs), \
                                 func.max(measurement.tobs), \
                                 func.avg(measurement.tobs).\
                                 after_start_date).all()
    session.close()

    return jsonify(start_results)

# When given the start and the end date, calculate the TMIN, TAVG, 
# and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startend():
    session = Session(engine)
    startend_results = session.query(func.min(measurement.tobs), \
                                 func.max(measurement.tobs), \
                                 func.avg(measurement.tobs), \
                                 filter(measurement.date.between(dt.date(2016,8,23), \
                                      dt.date(2017,8,23)))).all()
    session.close()

    return jsonify(startend_results)