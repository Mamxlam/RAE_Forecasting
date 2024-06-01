import pandas as pd
import lightgbm as lgb
import numpy as np
from datetime import timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error


# import debugpy
# debugpy.listen(5678)
# debugpy.wait_for_client()


def smape(preds, target):
    n = len(preds)
    masked_arr = ~((preds == 0) & (target == 0))
    preds, target = preds[masked_arr], target[masked_arr]
    num = np.abs(preds - target)
    denom = np.abs(preds) + np.abs(target)
    smape_val = (200 * np.sum(num / denom)) / n
    return smape_val


def lgbm_smape(preds, train_data):
    labels = train_data.get_label()
    smape_val = smape(preds, labels)
    return 'SMAPE', smape_val, False


from datetime import timedelta
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import numpy as np

def train_and_forecast(df, target_column, last_index, validity_offset_days=30*24):
    df = df.copy()

    # Ensure the index is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index, errors='coerce')

    validity_offset = timedelta(days=validity_offset_days)

    # Define the last date for the training set
    train_end_date = last_index - validity_offset

    # Split the data into training and validation sets
    train_df = df[df.index <= train_end_date]
    valid_df = df[(df.index > train_end_date) & (df.index <= last_index)]
    pred_df = df[(df.index > last_index)]

    # Features and target
    features = df.columns.difference([target_column])
    target_lbl = target_column

    X_train, y_train = train_df[features], train_df[target_lbl]
    X_valid, y_valid = valid_df[features], valid_df[target_lbl]
    X_pred = pred_df[features]

    # Fill NaN values with the average of their respective columns
    X_train = X_train.fillna(X_train.mean())
    X_valid = X_valid.fillna(X_valid.mean())
    X_pred = X_pred.fillna(X_pred.mean())

    # LightGBM dataset
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_valid, label=y_valid, reference=train_data)

    # Parameters
    params = {
        'objective': 'regression',
        'metric': 'mape',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.75,
        'bagging_fraction': 0.75,
        'early_stopping_rounds': 400,
        "force_col_wise": True,
        "verbose": 2
    }
    evaluation = lgb.log_evaluation(period=1, show_stdv=True)
    # Training
    num_boost_round = 1000

    bst = lgb.train(
        params,
        train_data,
        num_boost_round=num_boost_round,
        valid_sets=[valid_data, train_data],
        feval=lgbm_smape,
        callbacks=[evaluation],
    )

    # Predictions for the validation period
    y_valid_pred = bst.predict(X_valid, num_iteration=bst.best_iteration)

    # Evaluate RMSE
    rmse = mean_squared_error(y_valid, y_valid_pred, squared=False)
    print(f'Validation RMSE: {rmse}')

    # Evaluate MAPE
    mape = mean_absolute_percentage_error(y_valid, y_valid_pred)
    print(f'Validation MAPE: {mape}')

    # Evaluate MAPE
    mape_sum = mean_absolute_percentage_error([np.sum(y_valid)], [np.sum(y_valid_pred)])
    print(f'Validation MAPE Sum within window: {mape_sum}')

    smape_sum = smape([np.sum(y_valid_pred)], [np.sum(y_valid)]) / 100
    print(f'Validation SMAPE Sum within window: {smape_sum}')


    y_forecast_pred = bst.predict(X_pred, num_iteration=bst.best_iteration)

    # Combine the forecasts
    y_forecast = np.concatenate([y_valid_pred, y_forecast_pred])
    forecast_dates = np.concatenate([valid_df.index, pred_df.index])

    return y_forecast, forecast_dates, rmse, mape, mape_sum, smape_sum
