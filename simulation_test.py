import simpy
import random
import math

class WirelessAntenna:
    def __init__(self, env, name, transmission_rate, max_data_limit, x, y):
        self.env = env
        self.name = name
        self.transmission_rate = transmission_rate
        self.max_data_limit = max_data_limit
        self.current_data_usage = 0
        self.x = x
        self.y = y
        self.users_connected = []

    def connect_user(self, user):
        self.users_connected.append(user)
        print(f"{user.name} connected to antenna {self.name}")

    def transmit_data(self, user):
        if self.current_data_usage + user.data_to_send > self.max_data_limit:
            print(f"Antenna {self.name} has reached its maximum data limit. Redirecting {user.name} to another antenna.")
            return

        yield self.env.timeout(user.data_to_send / self.transmission_rate)
        self.current_data_usage += user.data_to_send
        print(f"{user.name} transmitted data through antenna {self.name} at time {self.env.now}")

class WirelessUser:
    def __init__(self, env, name, x, y, data_to_send, max_connection_time):
        self.env = env
        self.name = name
        self.x = x
        self.y = y
        self.data_to_send = data_to_send
        self.max_connection_time = max_connection_time

def distance(user, antenna):
    return math.sqrt((user.x - antenna.x)**2 + (user.y - antenna.y)**2)

def find_closest_available_antenna(user, antennas):
    available_antennas = [antenna for antenna in antennas if antenna.current_data_usage + user.data_to_send <= antenna.max_data_limit]
    if not available_antennas:
        return None
    return min(available_antennas, key=lambda antenna: distance(user, antenna))

def user_behavior(env, user, antennas):
    while True:
        closest_antenna = find_closest_available_antenna(user, antennas)
        if closest_antenna is None:
            print(f"No available antenna for {user.name}. Waiting...")
            yield env.timeout(1)
            continue

        closest_antenna.connect_user(user)
        yield env.process(closest_antenna.transmit_data(user))

        # Random time before disconnecting or moving
        connection_time = random.uniform(5, user.max_connection_time)
        yield env.timeout(connection_time)

        # Disconnect from the antenna
        closest_antenna.users_connected.remove(user)
        print(f"{user.name} disconnected from antenna {closest_antenna.name} at time {env.now}")

        # Move to a new location
        user.x = random.uniform(0, 10)
        user.y = random.uniform(0, 10)
        print(f"{user.name} moved to a new location at time {env.now}")

def power_consumption(env, antennas):
    while True:
        for antenna in antennas:
            # Power consumption is proportional to the current data load
            power_consumption_factor = antenna.current_data_usage / antenna.max_data_limit
            print(f"Antenna {antenna.name} power consumption: {power_consumption_factor * 100}% at time {env.now}")
            yield env.timeout(1)  # Adjust the interval for power consumption updates

# Simulation parameters
simulation_time = 50
num_antennas = 3
num_users_per_antenna = 3


# Run the simulation
env = simpy.Environment()

antennas = [
    WirelessAntenna(
        env=env, name=f"Antenna {i}", transmission_rate=random.uniform(0.5, 2.0), max_data_limit=random.uniform(20, 50), x=random.uniform(0, 10), y=random.uniform(0, 10))
    for i in range(num_antennas)
]

users = [
    WirelessUser(
        env=env, name=f"User {i}", x=random.uniform(0, 10), y=random.randint(0, 10), data_to_send=random.uniform(0, 10), max_connection_time=random.uniform(10, 20))
    for i in range(num_antennas * num_users_per_antenna)
]

for i in range(num_antennas):
    for j in range(num_users_per_antenna):
        antennas[i].connect_user(users[i * num_users_per_antenna + j])

env.process(power_consumption(env, antennas))

for user in users:
    env.process(user_behavior(env, user, antennas))

env.run(until=simulation_time)
