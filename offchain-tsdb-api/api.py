from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import configparser
import numpy as np

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Database connection details from config.ini
DB_HOST = config['database']['DB_HOST']
DB_NAME = config['database']['DB_NAME']
DB_USER = config['database']['DB_USER']
DB_PASSWORD = config['database']['DB_PASSWORD']
DB_PORT = config['database']['DB_PORT']

# Function to connect to the PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# Function to fetch all records from a specified table
def fetch_all_records(table_name, order_criteria):
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Prepare the query to fetch all records
        query = f"SELECT * FROM {table_name} ORDER BY {order_criteria} ASC;"

        # Execute the query
        cursor.execute(query)

        # Fetch all results
        records = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Convert numeric values to strings without scientific notation
        for record in records:
            for key, value in record.items():
                if isinstance(value, (int, float)):
                    record[key] = np.format_float_positional(value, trim='-')

        # Return the records as JSON
        return jsonify(records), 200
    except Exception as e:
        # In case of an error, return the error message
        return jsonify({"error": str(e)}), 500

# Function to handle common parameter validation and querying
def fetch_records(table_name, asset_id=None):
    try:
        # Get the end_time (Unix timestamp), limit, and scale from the query parameters
        end_time_str = request.args.get('end_time')
        limit = request.args.get('limit', default=40)  # Default limit is 40
        scale = request.args.get('scale', default='1m')  # Default scale is 1 minute

        # Validate limit parameter
        limit = int(limit)
        if limit <= 0:
            return jsonify({"error": "Limit must be a positive integer."}), 400

        # Validate end time parameter (should be a valid Unix timestamp)
        try:
            end_time_unix = int(end_time_str)
        except ValueError:
            return jsonify({"error": "Invalid Unix timestamp format."}), 400

        # Map scale values to a corresponding step (offset) and scale factor
        scale_mapping = {
            '1m': 1,     # every 1 minute
            '5m': 5,     # every 5 minutes
            '15m': 15,   # every 15 minutes
            '1h': 60,    # every 1 hour
            '12h': 720,  # every 12 hours
            '1d': 1440   # every 1 day
        }

        # Validate scale
        if scale not in scale_mapping:
            return jsonify({"error": "Invalid scale. Valid options are 1m, 5m, 15m, 1h, 12h, 1d."}), 400

        # Get the step value for the selected scale
        step = scale_mapping[scale]

        # Adjust the limit based on the scale
        adjusted_limit = limit * step

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Prepare the base query
        query = f"SELECT * FROM {table_name} WHERE time <= %s"

        # If asset_id is provided, add it to the query
        if asset_id is not None:
            query += " AND asset_id = %s"

        query += " ORDER BY time DESC LIMIT %s"

        # Execute the parameterized query
        if asset_id is not None:
            cursor.execute(query, (end_time_unix, asset_id, adjusted_limit))
        else:
            cursor.execute(query, (end_time_unix, adjusted_limit))

        # Fetch all results
        records = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Select every nth record from the fetched results based on the step value
        filtered_records = records[::step]  # Take every nth record where n is step

        # Convert numeric values to strings without scientific notation
        result = [
            [np.format_float_positional(value, trim='-') if isinstance(value, (int, float)) else value for value in record.values()]
            for record in filtered_records
        ]
 
        # Return the result as a list of lists
        return jsonify(result), 200
    except Exception as e:
        # In case of an error, return the error message
        return jsonify({"error": str(e)}), 500

# API route to get the last records from total_supply_borrow until a given end timestamp
@app.route('/api/total_supply_borrow', methods=['GET'])
def get_total_supply_borrow():
    return fetch_records("dashboard_total_supply_borrow")

# API route to get the last records from kylix_token until a given end timestamp
@app.route('/api/kylix_token', methods=['GET'])
def get_kylix_token():
    return fetch_records("dashboard_kylix_token")

# API route to get the last records from pool_data until a given end timestamp and asset_id
@app.route('/api/pools_data', methods=['GET'])
def get_pool_data():
    asset_id_str = request.args.get('asset_id')
    asset_id = None

    # Validate asset_id parameter
    if asset_id_str is not None:
        try:
            asset_id = int(asset_id_str)
            if asset_id < 0:
                return jsonify({"error": "Asset ID must be a non-negative integer."}), 400
        except ValueError:
            return jsonify({"error": "Invalid asset ID format."}), 400

    return fetch_records("pools_data", asset_id)

# API route to get all records from a specified table
@app.route('/api/interest_rate_model', methods=['GET'])
def get_table_data():
    return fetch_all_records("interest_rate_model", "utilization_rate")

# Main function to run the Flask app
if __name__ == '__main__':
    app.run(debug=False)
