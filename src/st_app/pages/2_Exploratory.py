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

from utils import get_aggregated_data, process_time_series, plot_columns_by_pattern, seasonal_decompose, plot_autocorrelation, plot_pautocorrelation

st.set_page_config(page_title="EDA Page", layout="wide")

st.title('Exploratory Data Analysis (EDA) Page 📊')


# Sidebar for input parameters
st.sidebar.header('Input Parameters')

# File uploader
st.sidebar.subheader('File Upload')
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    file_path = "cache/uploaded_file.csv"
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    # Section for frequency and dates
    st.sidebar.subheader('Aggregation Settings')
    frequency = st.sidebar.selectbox('Frequency', ['M'])
    current_date = st.sidebar.date_input('Current Date')
    forecast_horizon = st.sidebar.number_input('Forecast Horizon', min_value=1, max_value=60, value=12)

    if st.sidebar.button('Get Aggregated Data'):
        aggregated_data = get_aggregated_data(file_path, frequency, current_date.strftime('%Y-%m-%d'), forecast_horizon)
        if aggregated_data is not None:
            st.session_state.aggregated_data_available = True
            st.session_state.aggregated_data = aggregated_data

    if st.session_state.get('aggregated_data_available', False):
        if st.sidebar.button('Process Time Series'):
            result, extended_result = process_time_series('cache/agg_res.csv', current_date.strftime('%Y-%m-%d'), forecast_horizon)
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
    st.markdown("""
    The **Autocorrelation Function (ACF)** measures the correlation between a time series and its past values (lags). 
    It helps identify the extent to which current values of the series are influenced by past values. 
    Significant autocorrelation at lag k indicates that the series is k-period autocorrelated.
    """)
    acf_lags = st.slider('Select number of lags for ACF', min_value=1, max_value=120, value=30)
    acf_fig, acf_vals, acf_conf = plot_autocorrelation(extended_result[decompose_column], acf_lags)
    st.plotly_chart(acf_fig)

    # Partial Autocorrelation Plot
    st.subheader('Partial Autocorrelation Function (PACF)')
    st.markdown("""
    The **Partial Autocorrelation Function (PACF)** measures the direct effect of past values on the current value, 
    removing the effects of intermediate lags. It helps identify the specific lag values that are most influential 
    in the series without the influence of other lags. This is useful for determining the order of an ARIMA model.
    """)
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
