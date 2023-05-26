# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup - 10-Ins_Flask_with_ORM
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)



# Save references to each table
Measurement = Base.classes.measurements
Station = Base.classes.stations


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
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
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results from your precipitation analysis - 01-Ins_Joins
    # (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    session = Session(engine)
    results = (session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date))

    """Convert the query results from your precipitation analysis"""
    prcp_list = []
    for row in results:
        recent_dict = {}
        recent_dict["date"] = row.date
        recent_dict["tobs"] = row.tobs
        prcp_list.append(recent_dict)
           

    return jsonify(prcp_list)

    

@app.route("/api/v1.0/stations")
def stations():
    # # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

    


@app.route("/api/v1.0/tobs")
def tobs():
    # # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    # Query dates and temperature using the same query as with climate_starter
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    most_active = active_stations[0][0]
    active_12 = session.query(Measurement.station, Measurement.tobs).\
                filter(Measurement.station == most_active).\
                filter(Measurement.date >= (2016, 8, 23)).all()

     
    

    # Return a JSON list of temperature observations for the previous year.
    most_active_12 = list(np.ravel(active_12))

    return jsonify(most_active_12)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
"""
    # """For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.""" 
    spec_start = session.query(func.min(Measurement.tobs), 
                               func.avg(Measurement.tobs), 
                               func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    return jsonify(spec_start)


"""For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
"""
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    spec_start_end = session.query(func.min(Measurement.tobs), 
                                   func.avg(Measurement.tobs), 
                                   func.max(Measurement.tobs)).filter(Measurement.date) >= start.filter(Measurement.date <= end).all()
   

    return jsonify(spec_start_end)

if __name__ == '__main__':
    app.run(debug=True)
