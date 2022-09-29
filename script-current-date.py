from datetime import datetime, timedelta, date


now = datetime.now()

print("now is:")
print(now)


year = now.strftime("%Y")
print("year:", year)

month = now.strftime("%m")
print("month:", month)

day = now.strftime("%d")
print("day:", day)

formatted = now.strftime("%Y-%m-%d")
print("formatted:", formatted)


# Get today's date
today = date.today()
print("Today is: ", today)

# Yesterday date
yesterday = today - timedelta(days=1)
print("Yesterday was: ", yesterday)

formatted_yesterday = yesterday.strftime("%Y-%m-%d")
print("formatted_yesterday:", formatted_yesterday)
