# Data we could get:
# - Time
# - Connection State
# - Charging State
# - Battery Level
# - Charger Limit SOC
# - Battery Range
# - Charge Energy Added
# - Charge Rate
# - Charger Voltage
# - Charger Actual Current

# Data we can calculate:
# - Energy used
# - Energy prices
# - Charge Efficiency
import time
import csv
import argparse

from tesla_api import TeslaApiClient

# Interval for checks in seconds
INTERVAL = 60
# Needed to convert miles to km
CONVERSION_FACTOR = 0.62137119


def log_charge_state(car):
    charge_state = car.charge.get_state()
    print('Logging charge data... Current charge state: {}'.format(
        charge_state['charging_state'])
    )
    with open('charge_data.csv', 'a') as csv_file:
        csv.register_dialect('simple', lineterminator='\n')
        writer = csv.writer(csv_file, dialect='simple')
        writer.writerow([
            charge_state['timestamp'],
            car.state,
            charge_state['charging_state'],
            charge_state['battery_level'],
            charge_state['charge_limit_soc'],
            charge_state['battery_range'] / CONVERSION_FACTOR,
            charge_state['charge_energy_added'],
            charge_state['charge_rate'],
            charge_state['charger_voltage'],
            charge_state['charger_pilot_current']
        ])
    csv_file.close()


def update_vehicle():
    try:
        return api.list_vehicles()[0]
    except Exception as e:
        print('Got an exception while getting updated car state: {}'.format(str(e)))
    return None


def main():
    while True:
        # As we want checks to run exactly every INTERVAL seconds, we need to be able to count how
        # long we need to sleep.
        start_time = time.time()

        # We need to do this every loop iteration as this returns the current car state
        car = update_vehicle()

        if car is not None:
            print('Current car state: {}'.format(car.state))
            if car.state == 'online':
                log_charge_state(car)

        # Calculate and sleep the required amount of seconds so we have exactly INTERVAL seconds
        # between each check
        end_time = time.time()
        seconds_to_sleep = INTERVAL - (end_time - start_time)
        if seconds_to_sleep > 0:
            time.sleep(seconds_to_sleep)


def authenticate(username, password):
    client = TeslaApiClient(username, password)
    print("Authenticating...")
    client.authenticate()
    return client


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--tesla-username',
                        help='Tesla username needed to authenticate with the API',
                        required=True)
    parser.add_argument('--tesla-password',
                        help='Tesla password needed to authenticate with the API',
                        required=True)

    args = parser.parse_args()

    # First authenticate the API so we can use it in any of the functions
    api = authenticate(args.tesla_username, args.tesla_password)

    # Start the main loop
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown requested, exiting...")
        exit(0)
