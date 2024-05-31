import pandas as pd
import argparse

def aggregate_data(df, freq):
    # Aggregate data by the specified frequency
    aggregation = df.groupby(pd.Grouper(key='ΗΜΕΡΟΜΗΝΙΑ ΕΚΔ. ΑΔ.ΠΑΡΑΓΩΓΗΣ', freq=freq)).agg({
        'ΙΣΧΥΣ (MW)': ['count', 'sum', 'mean', 'min', 'max'],
        'RSI': ['mean', 'min', 'max'],
        'RSI_ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ': ['mean', 'min', 'max'],
        'RSI_ΔΗΜΟΣ ': ['mean', 'min', 'max'],
        'RSI_ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ': ['mean', 'min', 'max'],
        'RSI_ΘΕΣΗ': ['mean', 'min', 'max'],
    })

    aggregation = aggregation.dropna()

    # Extend DataFrame with future dates
    future_dates = pd.date_range(start=aggregation.index[-1], periods=48, freq=freq) + pd.DateOffset(**{freq: 1})
    future_index = pd.DatetimeIndex(future_dates)
    future_data = pd.DataFrame(index=future_index)

    # Concatenate current and future data
    aggregation = pd.concat([aggregation, future_data])

    # Flatten the multi-index columns
    aggregation.columns = ['_'.join(col).strip() for col in aggregation.columns.values]

    return aggregation

def main():
    parser = argparse.ArgumentParser(description="Aggregate MW data by a specified frequency.")
    parser.add_argument('input_file', type=str, help='Path to the input CSV file')
    parser.add_argument('output_file', type=str, help='Path to save the output CSV file')
    parser.add_argument('frequency', type=str, help='Frequency for aggregation (e.g., M for month, W for week, Q for quarter, Y for year)')

    args = parser.parse_args()

    # Load the input CSV file into a DataFrame
    df = pd.read_csv(args.input_file)

    # Perform aggregation
    result = aggregate_data(df, args.frequency)

    # Save the result to the output CSV file
    result.to_csv(args.output_file)

if __name__ == "__main__":
    main()
