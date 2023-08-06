import datetime
from datetime import datetime as dt

def find_monday_and_saturday(input_date):
    print(f'input date: {input_date}')
    print(f'')
    # Get the day of the week (0 = Monday, 6 = Sunday) for the input date
    day_of_week = input_date.weekday()


    # Calculate the number of days to subtract to get to Monday (assuming Monday is the first day of the week)
    days_to_monday = day_of_week

    # Calculate the number of days to add to get to Saturday (assuming Saturday is the last day of the week)
    days_to_saturday = 6 - day_of_week

    # Calculate the Monday and Saturday dates
    monday = input_date - datetime.timedelta(days=days_to_monday)
    saturday = input_date + datetime.timedelta(days=days_to_saturday)

    return monday, saturday

# Waktu indo
waktu_indo = dt.utcnow() + datetime.timedelta(hours=7)
format_waktu = waktu_indo.strftime("%H:%M:%S %Y-%m-%d ")
print(f'waktu indo sekarang: {format_waktu}')

# Input date (year, month, day)
input_date = datetime.date(2023, 8, 6)

# Find Monday and Saturday for the week containing the input date
monday, saturday = find_monday_and_saturday(input_date)

# Print the results
print("Input Date:", input_date)
print("Monday:", monday)
print("Saturday:", saturday)