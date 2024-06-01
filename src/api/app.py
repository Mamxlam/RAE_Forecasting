from flask import Flask, request, jsonify
import pandas as pd
from data_aggregator import aggregate_data, convert_to_datetime
from time_series_engineering import process_time_series
from forecasting_model import train_and_forecast

app = Flask(__name__)


# curl -X POST -F 'file=@all_ape_data_nodup_rsi.csv' -F 'frequency=M' -F 'current_date=2023-05-01' -F 'forecast_horizon=12' http://127.0.0.1:5000/aggregate > agg_res.csv
@app.route('/aggregate', methods=['POST'])
def aggregate():
    file = request.files['file']
    frequency = request.form.get('frequency')
    current_date = request.form.get('current_date')
    forecast_horizon = int(request.form.get('forecast_horizon', 48))  # Default to 48 if not provided

    if not file or not frequency or not current_date:
        return jsonify({'error': 'File, frequency, and current_date are required.'}), 400

    df = pd.read_csv(file)
    result = aggregate_data(df, frequency, current_date, forecast_horizon)
    result_csv = result.to_csv(index=True)
    
    return result_csv

# curl -X POST -F 'file=@agg_res.csv' -F 'current_date=2023-05-01' -F 'forecast_horizon=48' http://127.0.0.1:5000/process-time-series | jq -r '.result' > result.csv
# curl -X POST -F 'file=@agg_res.csv' -F 'current_date=2023-05-01' -F 'forecast_horizon=48' http://127.0.0.1:5000/process-time-series | jq -r '.extended_result' > extended_result.csv
@app.route('/process-time-series', methods=['POST'])
def process_time_series_route():
    file = request.files['file']
    current_date = request.form.get('current_date')
    forecast_horizon = int(request.form.get('forecast_horizon', 48))  # Default to 48 if not provided

    if not file or not current_date:
        return jsonify({'error': 'File and current_date are required.'}), 400

    df = pd.read_csv(file, parse_dates=True, index_col=0)
    result, extended_result = process_time_series(df, current_date, forecast_horizon)
    result_csv = result.to_csv(index=True)
    extended_result_csv = extended_result.to_csv(index=True)
    
    return jsonify({
        'result': result_csv,
        'extended_result': extended_result_csv
    })


# curl -X POST -F 'file=@extended_result.csv' -F 'target_column=ΙΣΧΥΣ (MW)_sum' -F 'last_index=2023-03-01' -F 'validity_offset_days=720' http://127.0.0.1:5000/forecast
@app.route('/forecast', methods=['POST'])
def forecast():
    file = request.files['file']
    target_column = request.form.get('target_column')
    last_index = request.form.get('last_index')
    validity_offset_days = int(request.form.get('validity_offset_days', 30*24))  # Default to 30 days

    if not file or not target_column or not last_index:
        return jsonify({'error': 'File, target_column, and last_index are required.'}), 400

    df = pd.read_csv(file, index_col=0, parse_dates=True)

    last_index = pd.to_datetime(last_index)

    y_forecast, forecast_dates, rmse, mape, mape_sum, smape_sum = train_and_forecast(df, target_column, last_index, validity_offset_days)
    
    return jsonify({
        'forecast': y_forecast.tolist(),
        'forecast_dates': forecast_dates.tolist(),
        'rmse': rmse,
        'mape': mape,
        'mape_sum': mape_sum,
        'smape_sum': smape_sum
    })

if __name__ == '__main__':
    app.run(debug=True)
