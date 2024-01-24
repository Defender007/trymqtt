reader_data = {
    "grant_type": "ACCESS_GRANTED",
    "uid": 123,
}

data_keys = [key for key in reader_data.keys()]

print(data_keys)


from datetime import datetime, timedelta

today = datetime.now().date()
start_of_month = today.replace(day=1)
print("Start of the Month: ", start_of_month)

start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

print("Start of the Week: ", start_of_week)
print("End of the Week: ", end_of_week)
