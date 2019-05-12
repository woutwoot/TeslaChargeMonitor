# TeslaChargeMonitor
A simple Python script to log data about Tesla charging sessions and parse it into electricity costs

Current limitations:
 - Only supports one car
 - Not sure about impact on phantom drain. Since the script only pulls data if the car is in the `online` state, 
 this script should have no effect on it, but I have not tested it extensively (yet)
 - Some values are hardcoded in the script (like cost per kWh) or always converted to metric. This should be easy to change

This is a small project with the intention of calculating the charging costs for my Tesla charge sessions.
To use this script run `worker.py` in a background session on a machine that is always online. 
I'm using `screen` to do so. (Tesla credentials are required, but only sent to Tesla as you can see in the code)
The script will log all charging data into a csv file `charge_data.csv`

When you want to calculate an overview of your charge sessions, just run `calculator.py` as 
this script will loop over the data in the csv file and make the neccecary calculations.
