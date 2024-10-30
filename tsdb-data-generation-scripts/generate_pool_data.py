import csv
import random
from datetime import datetime, timedelta

# Function to simulate supply/borrow data (minute-by-minute increments)
# IMPORTANT: It sometimes generates duplicate timestamps; just delete them from the csv or wait for the DB to tell you the duplicate at the time of the csv data insertion
def generate_data(asset_id, start_time, end_time):
    data = []
    
    # Calculate the number of minutes between start and end time
    num_minutes = int((end_time - start_time).total_seconds() // 60)
    
    # Initial values for total supply and total borrow
    initial_supply = 1000  # Starting value for total supply
    initial_borrow = 750   # Starting value for total borrow at 75% of initial supply
    
    # Define limits for supply and borrow based on ±25% of initial values
    min_supply = int(initial_supply * 0.75)
    max_supply = int(initial_supply * 1.25)
    max_borrow_ratio = 0.75  # Borrow cannot exceed 75% of supply

    total_supply = initial_supply
    total_borrow = min(int(total_supply * max_borrow_ratio), initial_borrow)

    for i in range(num_minutes):
        # Simulate time increments (1-minute intervals)
        timestamp = start_time + timedelta(minutes=i)
        
        # Update total supply within ±25% bounds of the initial supply
        supply_change = random.randint(-5, 5)
        total_supply = max(min_supply, min(max_supply, total_supply + supply_change))  # Keep total_supply within limits

        # Ensure total_borrow is capped at 75% of total_supply and also within ±25% bounds of the initial borrow
        max_borrow = int(total_supply * max_borrow_ratio)
        min_borrow = int(initial_borrow * 0.75)
        max_borrow_limit = int(initial_borrow * 1.25)

        borrow_change = random.randint(-3, 3)  # Small fluctuations
        total_borrow = max(min_borrow, min(max_borrow, min(max_borrow_limit, total_borrow + borrow_change)))

        # Convert timestamp to Unix time (seconds since epoch)
        unix_time = int(timestamp.timestamp())

        # Append the data point to the list
        data.append([asset_id, unix_time, total_borrow, total_supply])
    
    return data

# Write the data to a CSV file
def write_to_csv(filename, data):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["asset_id", "time", "total_borrow", "total_supply"])  # Header row without APY columns
        writer.writerows(data)

# Main function to generate data and write to CSV
def main():
    # Input for the start and end dates (must include time to the minute)
    asset_id = int(input("Enter asset ID (non-negative integer): "))
    start_date_str = input("Enter start date (YYYY-MM-DD HH:MM:00): ")
    end_date_str = input("Enter end date (YYYY-MM-DD HH:MM:00): ")
    
    # Parse the input dates
    start_time = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
    
    # Ensure end time is after start time
    if end_time <= start_time:
        print("Error: End time must be after start time.")
        return
    
    # Generate supply and borrow data between the start and end times
    data = generate_data(asset_id, start_time, end_time)
    
    # Write the data to a CSV file
    write_to_csv("pool_data_mock.csv", data)
    print(f"CSV file 'pool_data_mock.csv' generated successfully with data from {start_time} to {end_time}.")

if __name__ == "__main__":
    main()