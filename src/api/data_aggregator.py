import pandas as pd

def convert_to_datetime(df, columns=None):
    """
    Convert date-like columns in a DataFrame to datetime type.

    Parameters:
    df (DataFrame): Input DataFrame.
    columns (list of str, optional): List of columns to convert. 
                                     If None, attempts to convert all object type columns.

    Returns:
    DataFrame: DataFrame with date-like columns converted to datetime type.
    """
    # Copy the DataFrame to avoid modifying the original DataFrame
    df_copy = df.copy()
    
    # If no specific columns are provided, select all object type columns
    if columns is None:
        columns = df_copy.columns[df_copy.dtypes == 'object']
        df[columns] = df[columns].astype(str)
    
    # Iterate through each specified column
    for col in columns:
        print(f"Attempting column: {col}")
        # Check if the column can be converted to datetime
        try:

            # date1 = pd.to_datetime(df_copy[col], errors='coerce', format='%Y-%m-%d %H:%M:%S')
            # date2 = pd.to_datetime(df_copy[col], errors='coerce', format='%Y-%m-%d')

            # df[col] = date1.fillna(date2)
            df_copy[col]  = pd.to_datetime(df_copy[col], errors='coerce', format="mixed", dayfirst=True)
            print(f"Column {col} transformed successfully.\n")
        except Exception as e:
            print(f"Column {col} is incompatible with datetime: {e}\n")
            # If conversion fails, skip to the next column
            continue
            
    return df_copy

def aggregate_data(df, freq, current_date, forecast_horizon):

    df = convert_to_datetime(df, columns=['ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ ΑΙΤΗΣΗΣ', 'ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ', 'ΗΜΕΡΟΜΗΝΙΑ ΛΗΞΗΣ ΑΔ.ΠΑΡΑΓΩΓΗΣ'])

    aggregation = df.groupby(pd.Grouper(key='ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ', freq=freq)).agg({
        'ΙΣΧΥΣ (MW)': ['count', 'sum', 'mean', 'min', 'max'],
        'RSI': ['mean', 'min', 'max'],
        'RSI_ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ': ['mean', 'min', 'max'],
        'RSI_ΔΗΜΟΣ ': ['mean', 'min', 'max'],
        'RSI_ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ': ['mean', 'min', 'max'],
        'RSI_ΘΕΣΗ': ['mean', 'min', 'max'],
    })

    aggregation = aggregation.dropna()

    # Extend DataFrame with future dates based on the provided current date and forecast horizon
    future_dates = pd.date_range(start=current_date, periods=forecast_horizon, freq=freq)
    future_index = pd.DatetimeIndex(future_dates)
    future_data = pd.DataFrame(index=future_index)

    aggregation = pd.concat([aggregation, future_data])
    aggregation.columns = ['_'.join(col).strip() for col in aggregation.columns.values]

    return aggregation
