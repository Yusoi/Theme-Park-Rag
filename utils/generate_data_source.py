import os
import random
import uuid
from datetime import datetime, timedelta

import polars as pl

os.makedirs("events", exist_ok=True)
os.makedirs("customers", exist_ok=True)

# -----------------------------
# Configuration
# -----------------------------
START_DATE = datetime(2025, 1, 1)
NUM_DAYS = 365

BASE_VISITORS_PER_DAY = 2500

MAX_GROUP_SIZE = 5
MAX_RIDES_PER_VISITOR = 6

INDEPENDENT_PROB = 0.05

PARK_NAME = "WonderWorld"

RIDES = ["Roller Coaster", "Ferris Wheel", "Haunted House", "Water Rapids", "Drop Tower", "Bumper Cars", "Pirate Ship"]

RESTAURANTS = [
    "Pizza Palace",
    "Burger Barn",
    "Sushi Spot",
    "Taco Town",
    "Ice Cream Corner",
]

POPULARITY = {
    "Roller Coaster": (15, 50),
    "Ferris Wheel": (5, 15),
    "Haunted House": (10, 25),
    "Water Rapids": (10, 30),
    "Drop Tower": (12, 35),
    "Bumper Cars": (5, 20),
    "Pirate Ship": (5, 18),
}

PEAK_HOURS = [(12, 15)]

GENDERS = ["male", "female", "other"]


# -----------------------------
# Helpers
# -----------------------------
def visitors_for_day(date):
    base = BASE_VISITORS_PER_DAY

    # weekend boost
    if date.weekday() >= 5:
        base *= 1.4

    # random fluctuation
    noise = random.uniform(0.7, 1.3)

    return int(base * noise)


def is_peak_hour(dt):
    return any(start <= dt.hour < end for start, end in PEAK_HOURS)


def get_queue_time(ride, current_time):
    min_q, max_q = POPULARITY[ride]

    if is_peak_hour(current_time):
        max_q = int(max_q * 1.5)

    return random.randint(min_q, max_q)


def should_eat(current_time):
    h = current_time.hour

    if 11 <= h < 15:
        return random.random() < 0.7
    elif 18 <= h < 20:
        return random.random() < 0.4
    return random.random() < 0.15


def meal_duration():
    return random.randint(20, 60)


# -----------------------------
# Customer generation
# -----------------------------
def generate_group():
    group_id = str(uuid.uuid4())
    size = random.randint(1, MAX_GROUP_SIZE)

    group_type = random.choices(["family", "friends", "mixed"], weights=[0.5, 0.3, 0.2])[0]

    members = []

    for _ in range(size):
        vid = str(uuid.uuid4())

        if group_type == "family":
            age = random.choice([random.randint(5, 12), random.randint(30, 50)])
        elif group_type == "friends":
            age = random.randint(16, 35)
        else:
            age = random.randint(10, 60)

        members.append({"id": vid, "age": age, "gender": random.choice(GENDERS), "group_id": group_id})

    return members


# -----------------------------
# Session simulation
# -----------------------------
def generate_single_session(visitor_id, start_time, group_shift):
    events = []

    is_independent = random.random() < INDEPENDENT_PROB
    shift = random.randint(-15, 15) if is_independent else group_shift

    current_time = start_time + timedelta(minutes=shift)

    events.append({"id": visitor_id, "event_type": "park_entry", "datetime": current_time, "place": PARK_NAME})

    rides_sequence = random.sample(RIDES, random.randint(1, MAX_RIDES_PER_VISITOR))

    has_eaten = False

    for ride in rides_sequence:
        # restaurant
        if not has_eaten and should_eat(current_time):
            r = random.choice(RESTAURANTS)

            current_time += timedelta(minutes=random.randint(5, 15))

            events.append({"id": visitor_id, "event_type": "restaurant_entry", "datetime": current_time, "place": r})

            current_time += timedelta(minutes=meal_duration())

            events.append({"id": visitor_id, "event_type": "restaurant_exit", "datetime": current_time, "place": r})

            has_eaten = True

        # walk
        walk = random.randint(5, 25) if is_independent else random.randint(5, 15)
        current_time += timedelta(minutes=walk)

        # queue
        events.append({"id": visitor_id, "event_type": "ride_queue_entry", "datetime": current_time, "place": ride})

        q_time = get_queue_time(ride, current_time)

        if is_independent:
            q_time = int(q_time * random.uniform(0.7, 1.3))

        current_time += timedelta(minutes=q_time)

        events.append({"id": visitor_id, "event_type": "ride_entry", "datetime": current_time, "place": ride})

        current_time += timedelta(minutes=random.randint(3, 10))

        events.append({"id": visitor_id, "event_type": "ride_exit", "datetime": current_time, "place": ride})

    # late meal
    if not has_eaten and random.random() < 0.3:
        r = random.choice(RESTAURANTS)

        current_time += timedelta(minutes=5)

        events.append({"id": visitor_id, "event_type": "restaurant_entry", "datetime": current_time, "place": r})

        current_time += timedelta(minutes=meal_duration())

        events.append({"id": visitor_id, "event_type": "restaurant_exit", "datetime": current_time, "place": r})

    current_time += timedelta(minutes=random.randint(5, 30))

    events.append({"id": visitor_id, "event_type": "park_exit", "datetime": current_time, "place": PARK_NAME})

    return events, current_time


def generate_full_day(visitor_id, base_time, group_shift):
    events = []

    sessions = random.randint(1, 3)

    current_start = base_time

    for i in range(sessions):
        session_events, session_end = generate_single_session(visitor_id, current_start, group_shift)

        events.extend(session_events)

        if i < sessions - 1:
            gap = random.randint(30, 120)
            current_start = session_end + timedelta(minutes=gap)

    return events


# -----------------------------
# Main yearly generation
# -----------------------------
def generate_year():
    # Ensure directories exist
    os.makedirs("events", exist_ok=True)
    os.makedirs("customers", exist_ok=True)

    for d in range(NUM_DAYS):
        date = START_DATE + timedelta(days=d)

        customers = []
        events = []

        num_visitors = visitors_for_day(date)
        num_groups = max(1, num_visitors // 3)

        for _ in range(num_groups):
            group = generate_group()

            base_time = datetime(date.year, date.month, date.day, 9, 0, 0) + timedelta(minutes=random.randint(0, 10 * 60))

            group_shift = random.randint(-5, 5)

            for member in group:
                customers.append(member)

                events.extend(generate_full_day(member["id"], base_time, group_shift))

        events_df = pl.DataFrame(events).with_columns(pl.col("datetime").cast(pl.Datetime)).sort(["id", "datetime"])

        customers_df = pl.DataFrame(customers)

        date_str = date.strftime("%Y-%m-%d")

        events_path = f"events/date={date_str}"
        customers_path = f"customers/date={date_str}"

        # Create partition directories
        os.makedirs(events_path, exist_ok=True)
        os.makedirs(customers_path, exist_ok=True)

        # Write files
        events_df.write_parquet(f"{events_path}/data.parquet")
        customers_df.write_parquet(f"{customers_path}/data.parquet")

        print(f"{date_str} | visitors ~ {num_visitors} | events {events_df.height}")


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    generate_year()
