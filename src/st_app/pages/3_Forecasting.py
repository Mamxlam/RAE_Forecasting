import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import io
import random
import plotly.express as px
import lightgbm as lgb
import json

from utils import get_aggregated_data, process_time_series, forecast, plot_columns_by_pattern

st.set_page_config(page_title="Forecasting Page", layout="wide")
# Calculate figure width and height dynamically based on window width
WIN_WIDTH = st.sidebar.number_input('Enter window width (height is 40% of width)', value=1200)
FIG_WIDTH = 0.9 * WIN_WIDTH  # 90% of window width or maximum of 800 pixels
FIG_HEIGHT = 0.4 * FIG_WIDTH  # Maintain aspect ratio


# Streamlit App
st.title('Forecasting Page 📈')


def plot_feature_importance(feature_importance, model_name):
    feature_importance_df = pd.DataFrame(feature_importance, columns=['feature', 'importance'])
    feature_importance_df = feature_importance_df[feature_importance_df['importance']!=0]
    fig = px.bar(feature_importance_df, x='importance', y='feature', orientation='h', title=f'{model_name} Feature Importance')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig)

def save_model_to_json(bst):
    # Convert the model to a JSON-compatible dictionary
    model_dict = bst.dump_model()
    # Serialize the dictionary to a JSON string
    model_json = json.dumps(model_dict, indent=4)
    return model_json

# Sidebar for input parameters
st.sidebar.header('Input Parameters')
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    file_path = "cache/uploaded_file.csv"
    with open(file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.markdown("---")

    frequency = st.sidebar.selectbox('Frequency', ['M'])
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
            result, extended_result = process_time_series('cache/agg_res.csv', current_date.strftime('%Y-%m-%d'), forecast_horizon)
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
        # Example usage within the Streamlit app
        result_model1, result_model2, forecast_dates = forecast('cache/extended_result.csv', target_column, last_index.strftime('%Y-%m-%d'), validity_offset_days)
        if result_model1 and result_model2:
            st.session_state.model1_forecast_data, st.session_state.model1_rmse, st.session_state.model1_mape, st.session_state.model1_mape_sum, st.session_state.model1_smape_sum, st.session_state.model1_mdl = result_model1
            st.session_state.model2_forecast_data, st.session_state.model2_rmse, st.session_state.model2_mape, st.session_state.model2_mape_sum, st.session_state.model2_smape_sum, st.session_state.model2_mdl = result_model2
            st.session_state.forecast_dates = forecast_dates
            st.session_state.last_index = last_index

# Assuming the forecast function and other necessary imports are already defined

# Main content
if st.session_state.get('model1_forecast_data', False) and st.session_state.get('model2_forecast_data', False):
    # Add a radio button to select the model
    model_choice = st.radio(
        "Select Model",
        ('Original Model', 'Feature Selection Model')
    )

    if model_choice == 'Original Model':
        forecast_data = st.session_state.model1_forecast_data
        rmse = st.session_state.model1_rmse
        mape = st.session_state.model1_mape
        mape_sum = st.session_state.model1_mape_sum
        smape_sum = st.session_state.model1_smape_sum
        model = st.session_state.model1_mdl
    else:
        forecast_data = st.session_state.model2_forecast_data
        rmse = st.session_state.model2_rmse
        mape = st.session_state.model2_mape
        mape_sum = st.session_state.model2_mape_sum
        smape_sum = st.session_state.model2_smape_sum
        model = st.session_state.model2_mdl

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.extended_result.index, y=st.session_state.extended_result[target_column], mode='lines', name='Actual'))
    forecast_index = pd.to_datetime(st.session_state.forecast_dates)
    fig.add_trace(go.Scatter(x=forecast_index, y=forecast_data, mode='lines', name='Forecast'))

    # Add vertical line at last_index
    fig.add_shape(
        type="line",
        x0=st.session_state.last_index,
        y0=0,
        x1=st.session_state.last_index,
        y1=max(st.session_state.extended_result[target_column].max(), max(forecast_data)),
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
    st.metric('RMSE', rmse)
    st.metric('MAPE', mape)
    st.metric('MAPE Validity Summation Window', mape_sum)
    st.metric('SMAPE Validity Summation Window', smape_sum)




    # Add model selection and plotting logic
    if st.session_state.get('model1_mdl', False) and st.session_state.get('model2_mdl', False):

        if model_choice == 'Original Model':
            model = lgb.Booster(model_str=st.session_state.model1_mdl)
            print("Original model selected")
            feature_importance = list(zip(model.feature_name(), model.feature_importance()))
            plot_feature_importance(feature_importance, "Original Model")
        else:
            model = lgb.Booster(model_str=st.session_state.model2_mdl)
            print("Feat Select model selected")
            feature_importance = list(zip(model.feature_name(), model.feature_importance()))
            plot_feature_importance(feature_importance, "Feature Selection Model")

        model_json = save_model_to_json(model)
        with open('cache/model.json', 'w') as f:
            f.write(model_json)



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