import pandas as pd
import numpy as np
import requests
import io
import streamlit as st
import plotly.graph_objects as go
import statsmodels.api as sm

# Function to upload and get aggregated data from the API
def get_aggregated_data(file_path, frequency, current_date, forecast_horizon):
    url = 'http://127.0.0.1:5000/aggregate'
    files = {'file': open(file_path, 'rb')}
    data = {
        'frequency': frequency,
        'current_date': current_date,
        'forecast_horizon': forecast_horizon
    }
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        result = pd.read_csv(io.StringIO(response.text), index_col=0, parse_dates=True)
        result.to_csv('cache/agg_res.csv')  # Save the result as agg_res.csv in the cache folder
        return result
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

# Function to process time series data
def process_time_series(file_path, current_date, forecast_horizon):
    url = 'http://127.0.0.1:5000/process-time-series'
    files = {'file': open(file_path, 'rb')}
    data = {
        'current_date': current_date,
        'forecast_horizon': forecast_horizon
    }
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        json_response = response.json()
        result = pd.read_csv(io.StringIO(json_response['result']), index_col=0, parse_dates=True)
        extended_result = pd.read_csv(io.StringIO(json_response['extended_result']), index_col=0, parse_dates=True)
        extended_result.to_csv('cache/extended_result.csv')  # Save the extended result as extended_result.csv in the cache folder
        return result, extended_result
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None, None

# Function to forecast data
def forecast(file_path, target_column, last_index, validity_offset_days):
    url = 'http://127.0.0.1:5000/forecast'
    files = {'file': open(file_path, 'rb')}
    data = {
        'target_column': target_column,
        'last_index': last_index,
        'validity_offset_days': validity_offset_days
    }
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        json_response = response.json()
        forecast = json_response['forecast']
        rmse = json_response['rmse']
        mape = json_response['mape']
        mape_sum = json_response['mape_sum']
        smape_sum = json_response['smape_sum']
        forecast_dates = json_response['forecast_dates']
        return forecast, forecast_dates, rmse, mape, mape_sum, smape_sum
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None, None, None, None, None, None
    


def plot_columns_by_pattern(df, pattern, title="Plot of Columns Matching Pattern"):
    """
    Plot columns of a DataFrame that match a given regex pattern using Plotly.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data.
    - pattern (str): The regex pattern to match column names.
    - title (str): The title of the plot.

    Returns:
    - fig: Plotly figure object.
    """
    # Filter columns based on the regex pattern
    matching_columns = df.filter(regex=pattern).columns
    
    if len(matching_columns) == 0:
        raise ValueError(f"No columns match the pattern '{pattern}'")
    
    # Create a plotly figure
    fig = go.Figure()

    for col in matching_columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Index',
        yaxis_title='Values',
        template='plotly_dark'
    )
    
    return fig


def seasonal_decompose(df, column, model='additive', freq=None):
    """
    Perform seasonal decomposition on a DataFrame column.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data.
    - column (str): The column to decompose.
    - model (str): The type of seasonal decomposition. Either 'additive' or 'multiplicative'.
    - freq (str): Frequency string for resampling (e.g., 'M' for monthly).

    Returns:
    - decomposition: The seasonal decomposition result.
    """
    # Ensure the index is a DatetimeIndex and set the frequency
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    if freq:
        df = df.resample(freq).mean()

    print(df.head())
    df = df.asfreq(pd.infer_freq(df.index))

    if model == 'multiplicative':
        df[column] = df[column].loc[df[column] > 0]

    # Handle missing values
    df[column] = df[column].interpolate(method='linear').ffill().bfill()

    decomposition = sm.tsa.seasonal_decompose(df[column], model=model)
    return decomposition


def plot_autocorrelation(sales, lags, missing="drop"):
    """
    Plots the autocorrelation function of a time series and calculates the confidence interval.

    Args:
        sales (pd.Series): A pandas Series containing the time series data to plot.
        lags (int): The number of lags to include in the autocorrelation plot.

    Returns:
        tuple: A tuple containing the autocorrelation values and the confidence interval.
    """
    acf = sm.tsa.acf(sales, nlags=lags, missing=missing)

    # Calculate the confidence interval
    T = len(sales)
    conf_int = 2 / np.sqrt(T)

    # Create a bar plot using plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=np.arange(acf.size), y=acf))

    # Add the confidence interval lines
    fig.add_shape(
        type='line',
        x0=0, y0=conf_int, x1=lags, y1=conf_int,
        line=dict(color='blue', dash='dash')
    )
    fig.add_shape(
        type='line',
        x0=0, y0=-conf_int, x1=lags, y1=-conf_int,
        line=dict(color='blue', dash='dash')
    )

    # Update the layout
    fig.update_layout(
        xaxis=dict(title='Lag'),
        yaxis=dict(title='Autocorrelation'),
        title='Autocorrelation Plot'
    )

    return fig, acf, conf_int


def plot_pautocorrelation(sales, lags):
    """
    Plots the partial autocorrelation function of a time series and calculates the confidence interval.

    Args:
        sales (pd.Series): A pandas Series containing the time series data to plot.
        lags (int): The number of lags to include in the partial autocorrelation plot.

    Returns:
        tuple: A tuple containing the partial autocorrelation values and the confidence interval.
    """
    pacf = sm.tsa.pacf(sales.dropna(), nlags=lags)

    # Calculate the confidence interval
    T = len(sales)
    conf_int = 2 / np.sqrt(T)

    # Create a bar plot using plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=np.arange(pacf.size), y=pacf))

    # Add the confidence interval lines
    fig.add_shape(
        type='line',
        x0=0, y0=conf_int, x1=lags, y1=conf_int,
        line=dict(color='blue', dash='dash')
    )
    fig.add_shape(
        type='line',
        x0=0, y0=-conf_int, x1=lags, y1=-conf_int,
        line=dict(color='blue', dash='dash')
    )

    # Update the layout
    fig.update_layout(
        xaxis=dict(title='Lag'),
        yaxis=dict(title='Partial Autocorrelation'),
        title='Partial Autocorrelation Plot'
    )

    return fig, pacf, conf_int