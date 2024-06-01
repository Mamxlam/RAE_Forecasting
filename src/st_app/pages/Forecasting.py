import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import io
import random

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


# Sidebar for input parameters
st.sidebar.header('Input Parameters')
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    file_path = "uploaded_file.csv"
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.markdown("---")

    frequency = st.sidebar.selectbox('Frequency', ['M', 'Q', 'Y'])
    current_date = st.sidebar.date_input('Current Date')
    forecast_horizon = st.sidebar.number_input('Forecast Horizon', min_value=1, max_value=60, value=12)

    if st.sidebar.button('Get Aggregated Data'):
        aggregated_data = get_aggregated_data(file_path, frequency, current_date.strftime('%Y-%m-%d'), forecast_horizon)
        if aggregated_data is not None:
            st.write('Aggregated Data', aggregated_data.head())
            st.session_state.aggregated_data_available = True
            st.session_state.aggregated_data = aggregated_data

    if st.session_state.get('aggregated_data_available', False):
        if st.sidebar.button('Process Time Series'):
            result, extended_result = process_time_series('agg_res.csv', current_date.strftime('%Y-%m-%d'), forecast_horizon)
            if result is not None and extended_result is not None:
                st.write('Processed Time Series Data', result.head())
                st.write('Extended Time Series Data', extended_result.head())
                st.session_state.processed_data_available = True
                st.session_state.extended_result = extended_result

    # Check if processed data is available
    if st.session_state.get('processed_data_available', False):
        st.sidebar.markdown("---")
        extended_result = st.session_state.extended_result
        target_column = st.sidebar.selectbox('Target Column', extended_result.columns)
        last_index = st.sidebar.date_input('Validation Date Index', pd.to_datetime("2022-11-01"))
        validity_offset_days = st.sidebar.number_input('Validity Offset Days', min_value=1, value=360)

        if st.sidebar.button('Forecast'):
            st.sidebar.markdown("---")
            forecast_data, forecast_dates, rmse, mape, mape_sum, smape_sum = forecast('extended_result.csv', target_column, last_index.strftime('%Y-%m-%d'), validity_offset_days)
            if forecast_data is not None:
                st.session_state.forecast_data = forecast_data
                st.session_state.forecast_dates = forecast_dates
                st.session_state.rmse = rmse
                st.session_state.mape = mape
                st.session_state.mape_sum = mape_sum
                st.session_state.smape_sum = smape_sum
                st.session_state.last_index = last_index

# Main content
if st.session_state.get('forecast_data', False):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.extended_result.index, y=st.session_state.extended_result[target_column], mode='lines', name='Actual'))
    forecast_index = pd.to_datetime(st.session_state.forecast_dates)
    fig.add_trace(go.Scatter(x=forecast_index, y=st.session_state.forecast_data, mode='lines', name='Forecast'))

    # Add vertical line at last_index
    fig.add_shape(
        type="line",
        x0=st.session_state.last_index,
        y0=0,
        x1=st.session_state.last_index,
        y1=max(st.session_state.extended_result[target_column].max(), max(st.session_state.forecast_data)),
        line=dict(
            color="red",
            width=2,
            dash="dash",
        ),
    )
    fig.update_layout(title='Forecast vs Actual', xaxis_title='Date', yaxis_title=target_column)
    st.plotly_chart(fig)

    st.markdown("---")
    st.subheader('Forecast Metrics')
    st.metric('RMSE', st.session_state.rmse)
    st.metric('MAPE', st.session_state.mape)
    st.metric('MAPE Validity Summation Window', st.session_state.mape_sum)
    st.metric('SMAPE Validity Summation Window', st.session_state.smape_sum)


    st.markdown("---")
    st.subheader('Additional Insights')

    # Function to get a random sample of columns
    def get_random_columns(df, num_columns=50):
        return random.sample(list(df.columns), min(num_columns, len(df.columns)))

    # Button to regenerate random columns
    if st.button('Regenerate Random Columns'):
        st.session_state.random_columns = get_random_columns(st.session_state.extended_result)

    # Ensure random columns are initialized
    if 'random_columns' not in st.session_state:
        st.session_state.random_columns = get_random_columns(st.session_state.extended_result)

    # Preview of available columns
    st.write("Available columns preview (random 50):")
    random_columns = random.sample(list(st.session_state.extended_result.columns), min(50, len(st.session_state.extended_result.columns)))
    st.markdown(", ".join([f"`{col}`" for col in random_columns]))
    
    # Pattern input for additional insights
    pattern = st.text_input("Enter column name regex pattern for additional insights:")
    
    if pattern:
        try:
            additional_insights_fig = plot_columns_by_pattern(st.session_state.extended_result, pattern, title="Additional Insights")
            st.plotly_chart(additional_insights_fig)
        except ValueError as e:
            st.error(e)