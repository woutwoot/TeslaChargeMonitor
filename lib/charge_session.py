from datetime import datetime


class ChargeSession:

    def __init__(self):
        self.start = ''
        self.end = ''
        self.data = []

    def get_average_voltage(self):
        rows = len(self.data)
        total_voltage = 0
        for row in self.data:
            voltage = int(row[8])
            total_voltage += voltage
        return total_voltage / rows

    def __repr__(self):
        return str({
            'start': self.start,
            'end': self.end,
            'data': self.data
        })

    def get_charge_added(self):
        return float(self.data[-1][6])

    def get_power_used(self):
        return ((16 * 3 * 230) * self.get_charge_time()) / 1000

    def get_charge_efficiency(self):
        return (self.get_charge_added() / self.get_power_used()) * 100

    def get_charge_cost(self, price_per_kwh):
        return price_per_kwh * self.get_power_used()

    def get_charge_time(self):
        start = datetime.fromtimestamp(int(self.start) / 1000)
        end = datetime.fromtimestamp(int(self.end) / 1000)

        diff = end - start
        return diff.total_seconds() / 3600
