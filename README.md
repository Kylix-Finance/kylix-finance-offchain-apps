# Kylix-Finance Offchain Apps

This repository contains the following components for Kylix-Finance:

- **API**: Queries the TSDB (Time Series Database) and exposes the data in JSON format for the Frontend.
- **Data Generation Scripts**: Facilitates the easy mocking of data for the TSDB.
- **Service (TODO)**: Collects data from the node and inserts it into the TSDB.

## API Endpoints

The API is written in Python and provides the following three endpoints:

### 1. `/api/total_supply_borrow`

- **Method**: GET
- **Parameters**:
  - `end_time` (Unix timestamp): Specifies the end time for the data.
  - `limit` (integer): Represents the number of datasets (default: 40).
  - `scale` (string): Represents the time passed between two datasets. Valid options:
    - `1m` (1 minute)
    - `5m` (5 minutes)
    - `15m` (15 minutes)
    - `1h` (1 hour)
    - `12h` (12 hours)
    - `1d` (1 day)
  
- **Response**:
  - A JSON array with the following fields:
    - `unixtime`: Unix timestamp of the dataset.
    - `total_borrow`: Total borrow across all pools.
    - `total_supply`: Total supply across all pools.

### 2. `/api/kylix_token`

- **Method**: GET
- **Parameters**:
  - `end_time` (Unix timestamp): Specifies the end time for the data.
  - `limit` (integer): Represents the number of datasets (default: 40).
  - `scale` (string): Represents the time passed between two datasets. Valid options:
    - `1m` (1 minute)
    - `5m` (5 minutes)
    - `15m` (15 minutes)
    - `1h` (1 hour)
    - `12h` (12 hours)
    - `1d` (1 day)

- **Response**:
  - A JSON array with the following fields:
    - `unixtime`: Unix timestamp of the dataset.
    - `kylix_price`: The price of the Kylix token.

### 3. `/api/pools_data`

- **Method**: GET
- **Parameters**:
  - `end_time` (Unix timestamp): Specifies the end time for the data.
  - `limit` (integer): Represents the number of datasets (default: 40).
  - `scale` (string): Represents the time passed between two datasets. Valid options:
    - `1m` (1 minute)
    - `5m` (5 minutes)
    - `15m` (15 minutes)
    - `1h` (1 hour)
    - `12h` (12 hours)
    - `1d` (1 day)
  - `asset_id` (integer): The asset ID for which the results correspond.

- **Response**:
  - A JSON array with the following fields:
    - `asset_id`: The ID of the asset.
    - `unixtime`: Unix timestamp of the dataset.
    - `borrow_apy`: Borrow Annual Percentage Yield (APY) for the pool.
    - `supply_apy`: Supply Annual Percentage Yield (APY) for the pool.
    - `total_borrow`: Total borrow for the pool.
    - `total_supply`: Total supply for the pool.


## Service app(TODO)
---
