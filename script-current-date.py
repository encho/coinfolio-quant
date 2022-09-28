from datetime import datetime

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
