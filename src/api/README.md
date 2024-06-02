# RAE Forecasting API

This Flask API provides functionality for forecasting RAE (Random Awesome Events). It integrates with the data aggregator, forecasting model, and time series engineering modules to provide accurate predictions.

## Prerequisites

Before running the API, make sure you have the following installed:

- Python 3.x
- Flask
- Other dependencies mentioned in the `requirements.txt` file

## Installation

1. Clone the repository:

    ```shell
    git clone https://github.com/your-username/RAE_Forecasting.git
    ```

2. Navigate to the API directory:

    ```shell
    cd RAE_Forecasting/src/api
    ```

3. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```
    or 
    ```shell
    conda env create -f environment.yml
    ```

## Usage

To start the API, run the following command:

```shell
python3 app.py
```


## API Endpoints
This Flask API provides three main functionalities: aggregating time series data, processing time series data, and generating forecasts using a LightGBM model. Below is a detailed description of the API endpoints and their functionalities.

### 1. `/aggregate`
#### Method: POST
This endpoint aggregates time series data by a specified frequency and generates a DataFrame with aggregated results.

**Request Parameters:**
- `file` (form-data): The CSV file containing the time series data.
- `frequency` (form-data): The frequency for aggregation (e.g., `M` for month, `W` for week, `Q` for quarter, `Y` for year).
- `current_date` (form-data): The current date to start the forecast (format: `YYYY-MM-DD`).
- `forecast_horizon` (form-data): The forecast horizon (number of periods to forecast).

**Example Request:**
```sh
curl -X POST -F 'file=@agg_res.csv' -F 'frequency=M' -F 'current_date=2023-05-01' -F 'forecast_horizon=48' http://127.0.0.1:5000/aggregate
```

### 2. `/process-time-series`
#### Method: POST
This endpoint processes time series data by decomposing it into trend, seasonal, and residual components, and returns two DataFrames.

**Request Parameters:**

- `file` (form-data): The CSV file containing the time series data.
- `current_date` (form-data): The current date to start the forecast (format: `YYYY-MM-DD`).
- `forecast_horizon` (form-data): The forecast horizon (number of periods to forecast).

**Example Request:**
```sh
curl -X POST -F 'file=@agg_res.csv' -F 'current_date=2023-05-01' -F 'forecast_horizon=48' http://127.0.0.1:5000/process-time-series
```


**Example Response:**

```json
{
    "result": "CSV content here...",
    "extended_result": "CSV content here..."
}
```


### 3. `/forecast`
#### Method: POST
This endpoint generates forecasts using a LightGBM model based on the provided time series data.

**Request Parameters:**

- `file` (form-data): The CSV file containing the time series data.
- `target_column` (form-data): The name of the target column for forecasting.
- `last_index` (form-data): The last date of the time series data (format: YYYY-MM-DD).
- `validity_offset_days` (form-data): The number of days to offset for validation (default: 720).

**Example Request:**
```sh
curl -X POST -F 'file=@agg_res.csv' -F 'target_column=target' -F 'last_index=2023-05-01' -F 'validity_offset_days=720' http://127.0.0.1:5000/forecast
```

**Example Response:**
```json
{
    "forecast": [1.2, 1.5, 1.3, ...],
    "rmse": 0.25,
    "mape": 5.5
}
```

## Example Usage in Linux

To call the /process-time-series endpoint and save both returned CSVs:

```sh
response=$(curl -X POST -F 'file=@agg_res.csv' -F 'current_date=2023-05-01' -F 'forecast_horizon=48' http://127.0.0.1:5000/process-time-series)

echo "$response" | jq -r '.result' > result.csv
echo "$response" | jq -r '.extended_result' > extended_result.csv
```