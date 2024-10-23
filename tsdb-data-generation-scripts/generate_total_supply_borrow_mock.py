import csv
import random
from datetime import datetime, timedelta

# Function to simulate stock-like price movements (minute-by-minute increments)
def generate_data(start_time, end_time):
    data = []
    
    # Calculate the number of minutes between start and end time
    num_minutes = int((end_time - start_time).total_seconds() // 60)
    
    # Initial values for two arbitrary "stocks"
    supply = 100  # Arbitrary starting value for the larger stock
    borrow = 90   # Arbitrary starting value for the smaller stock

    for i in range(num_minutes):
        # Simulate time increments (1-minute intervals)
        timestamp = start_time + timedelta(minutes=i)
        
        # Stock A fluctuates more visibly, up or down by a larger range
        change_a = random.randint(-5, 5)  # Adjusted fluctuation range for minute intervals
        supply = max(0, supply + change_a)  # Ensure it doesn't drop below 0
        
        # Stock B is always smaller and fluctuates similarly
        # Ensure borrow remains less than supply and doesn't go negative
        borrow = max(0, supply - random.randint(5, 20))
        
        # Convert timestamp to Unix time (seconds since epoch)
        unix_time = int(timestamp.timestamp())

        # Append the data point to the list with integer values
        data.append([unix_time, supply, borrow])
    
    return data

# Write the data to a CSV file
def write_to_csv(filename, data):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["unix_time", "total_supply", "total_borrow"])  # Header row
        writer.writerows(data)

# Main function to generate data and write to CSV
def main():
    # Input for the start and end dates (must include time to the minute)
    start_date_str = input("Enter start date (YYYY-MM-DD HH:MM:00): ")
    end_date_str = input("Enter end date (YYYY-MM-DD HH:MM:00): ")
    
    # Parse the input dates
    start_time = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
    
    # Ensure end time is after start time
    if end_time <= start_time:
        print("Error: End time must be after start time.")
        return
    
    # Generate stock data between the start and end times
    data = generate_data(start_time, end_time)
    
    # Write the stock data to a CSV file
    write_to_csv("total_supply_borrow_mock.csv", data)
    print(f"CSV file 'total_supply_borrow_mock.csv' generated successfully with data from {start_time} to {end_time}.")

if __name__ == "__main__":
    main()