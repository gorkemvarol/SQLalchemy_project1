################################################
# IMPORT DEPENDENCIES
################################################
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
################################################
# DATABASE SETUP
################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
station = Base.classes.station

################################################
#FLASK SET UP
################################################
app = Flask(__name__)

################################################
#FLASK SET UP
###############################################

@app.route("/")
def welcome():
    """List available API routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #create session and query precipation and date data
    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

    #create dictionary from row data and append to a list
    precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip.append(precip_dict)
    
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    #create session to pull station information
    session = Session(engine)
    
    results2 = session.query(station.station).all()

    session.close()

#create dictionary from row data and append to a list
    stations = []
    for row in results2:
        station_dict = {}
        station_dict["station"] = row
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #create session to pull last year of data for most active station
    session = Session(engine)
    
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    results3 = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= one_year_ago).\
        filter(measurement.station =='USC00519281').all()

    session.close()

    #create dictionary from row data and append to a list
    tobs_list = []
    for date, tobs in results3:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_stats(start):
    """Pull temperature data for all dates greater than or equal to start date"""

    #create session to pull min, max, and avg temp and date data from start date
    session = Session(engine)

    results4 = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()

    session.close()

    # Create a dictionary to hold start data
    stats_start = []
    
    for min, avg, max in results4:
        stats_start_dict = {}
        stats_start_dict["min"] = min
        stats_start_dict["avg"] = avg
        stats_start_dict["max"] = max
        stats_start.append(stats_start_dict)
   
    return jsonify(stats_start)

@app.route("/api/v1.0/<start>/<end>")
def stat2(start, end):
    session=Session(engine)
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
    for dates between the start and end date inclusive."""

    results5 = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    session.close()

    # Create a dictionary to hold start/end data
    full_stats = []

    for min, avg, max in results5:
        full_stats_dict = {}
        full_stats_dict["min"] = min
        full_stats_dict["avg"] = avg
        full_stats_dict["max"] = max
        full_stats.append(full_stats_dict)

    return jsonify(full_stats)

if __name__ == '__main__':
    app.run(debug=True)