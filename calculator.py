# Read the charge log file, and try to find charge sessions.
# Use these to calculate electricity costs for charging
import csv

from lib.charge_session import ChargeSession

with open('charge_data.csv', 'r') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')

    # Parse CSV contents into separate charging sessions for easier calculations
    charge_sessions = []

    for row in reader:
        if row[1] == 'online' and row[2] == 'Charging':

            if len(charge_sessions) > 0 and charge_sessions[-1].end == '':
                charge_sessions[-1].data.append(row)
            else:
                charge_session = ChargeSession()
                charge_session.data.append(row)
                charge_session.start = row[0]
                charge_sessions.append(charge_session)

        elif len(charge_sessions) > 0 and charge_sessions[-1].end == '':
            charge_sessions[-1].end = row[0]

    count = 1
    for charge_session in charge_sessions:
        print('Charge session #{}'.format(count))
        print('  - Average voltage: {0:.1f}V'.format(charge_session.get_average_voltage()))
        print('  - Battery charge added: {} kWh'.format(charge_session.get_charge_added()))
        print('  - Power used: {0:.2f} kWh'.format(charge_session.get_power_used()))
        print('  - Charge efficiency: {0:.1f}%'.format(charge_session.get_charge_efficiency()))
        print('  - Charge cost: €{0:.2f}'.format(charge_session.get_charge_cost(0.25)))
        print('  - Charge time: {0:.2f}h'.format(charge_session.get_charge_time()))
        print()
        count += 1
