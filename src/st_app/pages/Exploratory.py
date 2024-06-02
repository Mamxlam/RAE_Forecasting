import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import io
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler
import random
import numpy as np

st.set_page_config(page_title="EDA Page", layout="wide")

st.title('Exploratory Data Analysis (EDA) Page 📊')

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

    df = df.asfreq(pd.infer_freq(df.index))
    
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





# Sidebar for input parameters
st.sidebar.header('Input Parameters')

# File uploader
st.sidebar.subheader('File Upload')
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    file_path = "uploaded_file.csv"
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # Section for frequency and dates
    st.sidebar.subheader('Aggregation Settings')
    frequency = st.sidebar.selectbox('Frequency', ['M', 'Q', 'Y'])
    current_date = st.sidebar.date_input('Current Date')
    forecast_horizon = st.sidebar.number_input('Forecast Horizon', min_value=1, max_value=60, value=12)

    if st.sidebar.button('Get Aggregated Data'):
        aggregated_data = get_aggregated_data(file_path, frequency, current_date.strftime('%Y-%m-%d'), forecast_horizon)
        if aggregated_data is not None:
            st.session_state.aggregated_data_available = True
            st.session_state.aggregated_data = aggregated_data

    if st.session_state.get('aggregated_data_available', False):
        if st.sidebar.button('Process Time Series'):
            result, extended_result = process_time_series('agg_res.csv', current_date.strftime('%Y-%m-%d'), forecast_horizon)
            if result is not None and extended_result is not None:
                st.session_state.processed_data_available = True
                st.session_state.extended_result = extended_result

# Main content
if st.session_state.get('processed_data_available', False):
    extended_result = st.session_state.extended_result.dropna()

    # Time Series Plot
    st.subheader('Time Series Plot')
    column_to_plot = st.selectbox('Select column to plot:', extended_result.columns)
    fig = px.line(extended_result, x=extended_result.index, y=column_to_plot, title=f'Time Series Plot for {column_to_plot}')
    st.plotly_chart(fig)

    # Histogram
    st.subheader('Histogram')
    column_for_histogram = st.selectbox('Select column for histogram:', extended_result.columns, key='histogram')
    fig_hist = px.histogram(extended_result, x=column_for_histogram, nbins=50, title=f'Histogram for {column_for_histogram}')
    st.plotly_chart(fig_hist)

    # Correlation Heatmap
    st.subheader('Correlation Heatmap')

    # Allow user to select the target column to always include
    target_column_for_corr = st.selectbox('Select a target column to always include in the correlation heatmap', extended_result.columns)

    # Slider to select the number of columns to sample
    num_columns_to_sample = st.slider('Number of columns to sample for correlation heatmap (including the target column)', min_value=3, max_value=50, value=20)

    # Ensure the target column is always included
    if target_column_for_corr:
        available_columns = [col for col in extended_result.columns if col != target_column_for_corr]
        num_random_columns = num_columns_to_sample - 1  # Reserve one spot for the target column
        
        if len(available_columns) > num_random_columns:
            sampled_columns = random.sample(available_columns, num_random_columns)
            sampled_columns = [target_column_for_corr] + sampled_columns  # Prepend target column
            corr = extended_result[sampled_columns].corr()
        else:
            st.warning("Not enough columns to sample. Showing correlation for all available columns.")
            corr = extended_result.corr()
    else:
        corr = extended_result.corr()

    fig_corr = px.imshow(corr, text_auto=True, aspect='auto', title='Correlation Heatmap')
    st.plotly_chart(fig_corr)




# Seasonal Decomposition
    st.subheader('Seasonal Decomposition')
    decompose_column = st.selectbox('Select column for seasonal decomposition:', extended_result.columns, key='decompose')
    decompose_model = st.selectbox('Select decomposition model:', ['additive', 'multiplicative'])
    decompose_freq = st.selectbox('Select frequency for decomposition:', ['M', 'Q', 'Y'], index=0)  # Monthly, Quarterly, Yearly
    decomposition = seasonal_decompose(extended_result, decompose_column, decompose_model, freq=decompose_freq)

    st.write("Trend")
    st.line_chart(decomposition.trend)

    st.write("Seasonal")
    st.line_chart(decomposition.seasonal)

    st.write("Residual")
    st.line_chart(decomposition.resid)



    # Autocorrelation Plot
    st.subheader('Autocorrelation Function (ACF)')
    acf_lags = st.slider('Select number of lags for ACF', min_value=1, max_value=120, value=30)
    acf_fig, acf_vals, acf_conf = plot_autocorrelation(extended_result[decompose_column], acf_lags)
    st.plotly_chart(acf_fig)

    # Partial Autocorrelation Plot
    st.subheader('Partial Autocorrelation Function (PACF)')
    pacf_lags = st.slider('Select number of lags for PACF', min_value=1, max_value=120, value=30)
    pacf_fig, pacf_vals, pacf_conf = plot_pautocorrelation(extended_result[decompose_column], pacf_lags)
    st.plotly_chart(pacf_fig)

    # Preview of available columns
    st.subheader('Preview Available Columns')
    random_columns = random.sample(list(extended_result.columns), min(50, len(extended_result.columns)))
    random_columns_df = extended_result[random_columns].head()
    st.dataframe(random_columns_df)

    # Pattern input for additional insights
    st.subheader('Additional Insights')
    pattern = st.text_input("Enter column name pattern for additional insights:")
    
    if pattern:
        try:
            additional_insights_fig = plot_columns_by_pattern(extended_result, pattern, title="Additional Insights")
            st.plotly_chart(additional_insights_fig)
        except ValueError as e:
            st.error(e)
