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
from datetime import datetime

from tesla_api import TeslaApiClient

# Interval for checks in seconds
INTERVAL = 60
# Needed to convert miles to km
CONVERSION_FACTOR = 0.62137119

# Time needed without API requests for the car to allow sleeping
MIN_TIME_TO_SLEEP = 60 * 11  # 11 minutes


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
    return charge_state


def update_vehicle():
    try:
        return api.list_vehicles()[0]
    except Exception as e:
        print('Got an exception while getting updated car state: {}'.format(str(e)))
    return None


def main():
    should_sleep = False
    # We will count sleep time where we did not do a data request here
    total_sleep_time = 0

    while True:
        # As we want checks to run exactly every INTERVAL seconds, we need to be able to count how
        # long we need to sleep.
        start_time = time.time()

        # We need to do this every loop iteration as this returns the current car state
        car = update_vehicle()

        if car is not None:
            print('Current car state: {}'.format(car.state))

            # The car is online, but us getting data from the car will also keep it online. In this
            # case we need to try to detect that a charge is not going to happen soon and stop
            # requesting charging data so the car can go to sleep.
            if car.state == 'online':

                if should_sleep:
                    print('We\'re trying to have the car sleep. We\'ve waited {} minutes so far.'
                          .format(total_sleep_time / 60))
                else:
                    charge_state = log_charge_state(car)
                    print('Current charge state: {}'.format(charge_state['charging_state']))

                    if charge_state['charging_state'] == 'Complete':
                        should_sleep = True
                        print('Charging complete. Will not poll data so car can sleep.')

                    if charge_state['charging_state'] == 'Stopped':

                        if charge_state['scheduled_charging_pending']:
                            charge_start_date = datetime.fromtimestamp(
                                int(charge_state['scheduled_charging_start_time']))
                            print('A charge is planned to start later. ({})'.format(
                                str(charge_start_date)[:19]))

                            now = datetime.now()
                            if (charge_start_date - now).total_seconds() > MIN_TIME_TO_SLEEP:
                                should_sleep = True
                                print('Will stop polling now as this is more than 11 minutes '
                                      'from now.')

            elif car.state == 'asleep':
                # We've manged to sleep, so we can reset this now as we will not log anything until
                # the car wakes up again
                should_sleep = False
                total_sleep_time = 0

        # Calculate and sleep the required amount of seconds so we have exactly INTERVAL seconds
        # between each check
        end_time = time.time()
        seconds_to_sleep = INTERVAL - (end_time - start_time)
        if seconds_to_sleep > 0:
            total_sleep_time += INTERVAL
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
