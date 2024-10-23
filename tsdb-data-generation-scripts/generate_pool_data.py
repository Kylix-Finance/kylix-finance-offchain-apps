import csv
import random
from datetime import datetime, timedelta

# Function to simulate APY and supply/borrow data (minute-by-minute increments)
# IMPORTANT: It sometimes generates duplicate timestamps, just delete them from the csv or wait for the DB to tell you the duplicate at the time of the csv data insertion
def generate_data(asset_id, start_time, end_time):
    data = []
    
    # Calculate the number of minutes between start and end time
    num_minutes = int((end_time - start_time).total_seconds() // 60)
    
    # Initial values for total supply and total borrow
    total_supply = 1000  # Arbitrary starting value for total supply
    total_borrow = 900   # Arbitrary starting value for total borrow

    # Ensure initial values are greater than 0
    total_supply = max(1, total_supply)  # Ensure total_supply is greater than 0
    total_borrow = max(1, total_borrow)   # Ensure total_borrow is greater than 0

    # Initial APY values
    previous_supply_apy = round(random.uniform(0.01, 1), 3)  # Start with a supply_apy greater than 0
    previous_borrow_apy = round(random.uniform(0.01, previous_supply_apy), 3)  # Start with borrow_apy less than supply_apy

    for i in range(num_minutes):
        # Simulate time increments (1-minute intervals)
        timestamp = start_time + timedelta(minutes=i)
        
        # Simulate supply APY tendency (it can increase or decrease)
        supply_change = random.uniform(-0.01, 0.01)  # Small change
        new_supply_apy = round(max(0.01, min(1, previous_supply_apy + supply_change)), 3)  # Ensure it's > 0

        # Update borrow_apy based on the new supply_apy while keeping it lower or equal
        new_borrow_apy = round(random.uniform(0.01, new_supply_apy), 3)  # Ensure it's > 0 and less than or equal to new supply_apy
        
        # Update total supply and total borrow based on some random fluctuation
        total_supply += random.randint(-5, 5)
        total_supply = max(1, total_supply)  # Ensure total_supply is greater than 0
        
        total_borrow = max(1, total_supply - random.randint(0, 200))  # Ensure borrow does not exceed supply and is greater than 0

        # Convert timestamp to Unix time (seconds since epoch)
        unix_time = int(timestamp.timestamp())

        # Append the data point to the list
        data.append([asset_id, unix_time, new_borrow_apy, new_supply_apy, total_borrow, total_supply])
        
        # Update previous values for the next iteration
        previous_supply_apy = new_supply_apy
        previous_borrow_apy = new_borrow_apy
    
    return data

# Write the data to a CSV file
def write_to_csv(filename, data):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["asset_id", "time", "borrow_apy", "supply_apy", "total_borrow", "total_supply"])  # Header row
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
    
    # Generate APY data between the start and end times
    data = generate_data(asset_id, start_time, end_time)
    
    # Write the APY data to a CSV file
    write_to_csv("pool_data_mock.csv", data)
    print(f"CSV file 'pool_data_mock.csv' generated successfully with data from {start_time} to {end_time}.")

if __name__ == "__main__":
    main()