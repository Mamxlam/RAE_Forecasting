
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Forecasting Page", layout="wide")
# Calculate figure width and height dynamically based on window width
WIN_WIDTH = st.sidebar.number_input('Enter window width (height is 40% of width)', value=1200)
FIG_WIDTH = 0.9 * WIN_WIDTH  # 90% of window width or maximum of 800 pixels
FIG_HEIGHT = 0.4 * FIG_WIDTH  # Maintain aspect ratio


# Streamlit App
st.title('Forecasting Page 📈')

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
        return forecast, rmse, mape
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None, None, None

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    file_path = "uploaded_file.csv"
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # Sidebar for input parameters
    st.sidebar.header('Input Parameters')
    frequency = st.sidebar.selectbox('Frequency', ['M', 'Q', 'Y'])
    current_date = st.sidebar.date_input('Current Date')
    forecast_horizon = st.sidebar.number_input('Forecast Horizon', min_value=1, max_value=60, value=12)

    # Button to get aggregated data
    if st.sidebar.button('Get Aggregated Data'):
        aggregated_data = get_aggregated_data(file_path, frequency, current_date.strftime('%Y-%m-%d'), forecast_horizon)
        if aggregated_data is not None:
            st.write('Aggregated Data', aggregated_data.head())

            # Save aggregated data to CSV for the next API call
            aggregated_data.to_csv('agg_res.csv', index=True)
            st.session_state.aggregated_data_available = True
            st.session_state.aggregated_data = aggregated_data

    # Check if aggregated data is available
    if st.session_state.get('aggregated_data_available', False):
        # Button to process time series
        if st.sidebar.button('Process Time Series'):
            result, extended_result = process_time_series('agg_res.csv', current_date.strftime('%Y-%m-%d'), forecast_horizon)
            if result is not None and extended_result is not None:
                st.write('Processed Time Series Data', result.head())
                st.write('Extended Time Series Data', extended_result.head())

                # Save extended result to CSV for the next API call
                extended_result.to_csv('extended_result.csv', index=True)
                st.session_state.processed_data_available = True
                st.session_state.extended_result = extended_result

    # Check if processed data is available
    if st.session_state.get('processed_data_available', False):
        extended_result = st.session_state.extended_result
        target_column = st.sidebar.selectbox('Target Column', extended_result.columns)
        last_index = st.sidebar.date_input('Last Index')
        validity_offset_days = st.sidebar.number_input('Validity Offset Days', min_value=1, value=720)

        # Button to forecast
        if st.sidebar.button('Forecast'):
            forecast_data, rmse, mape = forecast('extended_result.csv', target_column, last_index.strftime('%Y-%m-%d'), validity_offset_days)
            if forecast_data is not None:
                st.write(f'RMSE: {rmse}')
                st.write(f'MAPE: {mape}')

                # Plot the forecast
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=extended_result.index, y=extended_result[target_column], mode='lines', name='Actual'))
                forecast_index = pd.date_range(start=last_index, periods=len(forecast_data), freq='M')
                fig.add_trace(go.Scatter(x=forecast_index, y=forecast_data, mode='lines', name='Forecast'))
                fig.update_layout(title='Forecast vs Actual', xaxis_title='Date', yaxis_title=target_column)
                st.plotly_chart(fig)

                # Additional insights
                st.subheader('Additional Insights')
                st.write('Any other insights related to the generated forecast can be included here.')