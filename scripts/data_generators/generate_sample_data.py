import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
import random

N = 10000

users = [f"user_{i}" for i in range(1, 201)]
devices = ["mobile", "desktop", "tablet"]
cities = ["New York", "London", "Tokyo", "Berlin", None]

rows = []

start = datetime.now() - timedelta(days=30)

for i in range(N):

    event_time = start + timedelta(
        seconds=random.randint(0, 30*24*3600)
    )

    rows.append({
        "event_id": str(uuid.uuid4()),
        "user_id": random.choice(users),
        "session_id": f"s_{random.randint(1,1000)}",
        "device_type": random.choice(devices),
        "geo_city": random.choice(cities),
        "event_timestamp": event_time
    })

df = pd.DataFrame(rows)

df.to_csv("data/raw/sample_user_events.csv", index=False)

print("Dataset created:", df.shape)