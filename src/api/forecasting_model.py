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


def evaluate_model(y_valid, y_valid_pred):
    rmse = mean_squared_error(y_valid, y_valid_pred, squared=False)
    print(f'Validation RMSE: {rmse}')

    mape = mean_absolute_percentage_error(y_valid, y_valid_pred)
    print(f'Validation MAPE: {mape}')

    mape_sum = mean_absolute_percentage_error([np.sum(y_valid)], [np.sum(y_valid_pred)])
    print(f'Validation MAPE Sum within window: {mape_sum}')

    smape_sum = smape([np.sum(y_valid_pred)], [np.sum(y_valid)]) / 100
    print(f'Validation SMAPE Sum within window: {smape_sum}')

    return rmse, mape, mape_sum, smape_sum


def train_and_forecast(df, target_column, last_index, validity_offset_days=30*24, top_k=20):
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


    # Clear dataframe from possible target columns 
    # List of columns to drop if found
    columns_to_drop = [
        'ΙΣΧΥΣ (MW)_count', 'ΙΣΧΥΣ (MW)_sum', 'ΙΣΧΥΣ (MW)_mean', 'ΙΣΧΥΣ (MW)_min', 'ΙΣΧΥΣ (MW)_max',
        'RSI_mean', 'RSI_min', 'RSI_max', 
        'RSI_ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ_mean', 'RSI_ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ_min', 'RSI_ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ_max',
        'RSI_ΔΗΜΟΣ _mean', 'RSI_ΔΗΜΟΣ _min', 'RSI_ΔΗΜΟΣ _max',
        'RSI_ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ_mean', 'RSI_ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ_min', 'RSI_ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ_max',
        'RSI_ΘΕΣΗ_mean', 'RSI_ΘΕΣΗ_min', 'RSI_ΘΕΣΗ_max'
    ]

    # Drop specified columns if they exist
    X_train = X_train.drop(columns=[col for col in columns_to_drop if col in X_train.columns])
    X_valid = X_valid.drop(columns=[col for col in columns_to_drop if col in X_valid.columns])
    X_pred = X_pred.drop(columns=[col for col in columns_to_drop if col in X_pred.columns])

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

    bst1 = lgb.train(
        params,
        train_data,
        num_boost_round=num_boost_round,
        valid_sets=[valid_data, train_data],
        feval=lgbm_smape,
        callbacks=[evaluation],
    )

    feature_importance = bst1.feature_importance(importance_type='gain')
    feature_names = X_train.columns
    feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': feature_importance})
    feature_importance_df = feature_importance_df.sort_values(by='importance', ascending=False)
    feature_importance_df = feature_importance_df[feature_importance_df['importance']!=0]
    
    top_100_features = feature_importance_df['feature'].head(top_k).tolist()

    X_train_top100 = X_train[top_100_features]
    X_valid_top100 = X_valid[top_100_features]
    X_pred_top100 = X_pred[top_100_features]

    train_data_top100 = lgb.Dataset(X_train_top100, label=y_train)
    valid_data_top100 = lgb.Dataset(X_valid_top100, label=y_valid, reference=train_data_top100)

    bst2 = lgb.train(
        params,
        train_data_top100,
        num_boost_round=num_boost_round,
        valid_sets=[valid_data_top100, train_data_top100],
        feval=lgbm_smape,
        callbacks=[evaluation],
    )

    y_valid_pred1 = bst1.predict(X_valid, num_iteration=bst1.best_iteration)
    y_valid_pred2 = bst2.predict(X_valid_top100, num_iteration=bst2.best_iteration)

    rmse1, mape1, mape_sum1, smape_sum1 = evaluate_model(y_valid, y_valid_pred1)
    rmse2, mape2, mape_sum2, smape_sum2 = evaluate_model(y_valid, y_valid_pred2)

    y_forecast_pred1 = bst1.predict(X_pred, num_iteration=bst1.best_iteration)
    y_forecast_pred2 = bst2.predict(X_pred_top100, num_iteration=bst2.best_iteration)

    y_forecast1 = np.concatenate([y_valid_pred1, y_forecast_pred1])
    y_forecast2 = np.concatenate([y_valid_pred2, y_forecast_pred2])
    forecast_dates = np.concatenate([valid_df.index, pred_df.index])
    print(feature_importance_df.head(top_k))

    return (bst1.model_to_string(), y_forecast1, rmse1, mape1, mape_sum1, smape_sum1), (bst2.model_to_string(), y_forecast2, rmse2, mape2, mape_sum2, smape_sum2), forecast_dates

