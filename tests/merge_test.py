import numpy as np
import pandas as pd
import seaborn as sns
import os

# import debugpy
# debugpy.listen(5678)
# debugpy.wait_for_client()


def merge_dataframes(df1, df2):
    """
    Merge the first 13 columns of two DataFrames.

    Parameters:
    df1 (DataFrame): First DataFrame.
    df2 (DataFrame): Second DataFrame.

    Returns:
    DataFrame: Merged DataFrame containing the first 13 columns of each DataFrame.

    Example:
        >>> df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> df2 = pd.DataFrame({'A': [7, 8, 9], 'C': [10, 11, 12]})
        >>> merge_dataframes(df1, df2)
           A  B   C
        0  1  4  10
        1  2  5  11
        2  3  6  12
    """
    # Determine the number of columns to merge (minimum between the two DataFrames)
    for col in df2.columns:
        if df2[col].dtype == 'datetime64[ns]':
            df2[col] = df2[col].dt.strftime('%Y-%m-%d')

    for col in df1.columns:
        if df1[col].dtype == 'datetime64[ns]':
            df1[col] = df1[col].dt.strftime('%Y-%m-%d')

    common_columns = df1.columns.intersection(df2.columns)

    merged_df = df1.merge(df2, on=common_columns.tolist(), how='outer')

    return merged_df

def merge_dataframes_with_previous_files(file_paths, column_patterns):
    """
    Merge the first 13 columns of DataFrames from multiple Excel files with two sheets each.
    The column names from the first DataFrame are kept.

    Parameters:
    file_paths (list): List of file paths to Excel files.

    Returns:
    DataFrame: Merged DataFrame containing the first 13 columns of each DataFrame from all files.
    """
    merged_df = None

    # Iterate over each file path
    for file_path in file_paths:
        merged_df_temp = None
        print(f"\nLoading file : {file_path}")
        # Load Excel file into separate DataFrames
        # Fetch only first sheet as it is RES 
        df = pd.read_excel(file_path, header=1, sheet_name=[0], parse_dates=False)
        print(f"Number of sheets detected: {len(df.keys())}")

        # Merge in sheet level
        for sheet_name, df_sheet in df.items():
            print(f"Number of rows detected: {len(df_sheet)}")
            # Filter according to pattern columns to keep
            df_sheet = df_sheet.filter(regex='|'.join(column_patterns))
            df_sheet['file'] = file_path
            print(f"Number of columns detected in {sheet_name} : {len(df_sheet.columns)}")
            if merged_df_temp is None:
                # Merge the Sheet DataFrames
                merged_df_temp = df_sheet
            else:
                merged_df_temp = merge_dataframes(merged_df_temp, df_sheet)

        # Merge in file level
        # If merged_df is None, assign it the merged DataFrame, else merge with the previous merged DataFrame
        if merged_df is None:
            merged_df = merged_df_temp
        else:
            merged_df = merge_dataframes(merged_df, merged_df_temp)
        
        print(f"Number of rows detected after merge: {len(merged_df)}")

    return merged_df

def fillna_column(df, column_name, fillna_column_name):
    """
    Fill missing values in a column by using values from another column.

    Args:
        df (pandas.DataFrame): The DataFrame containing the columns.
        column_name (str): The name of the column to fill missing values.
        fillna_column_name (str): The name of the column to use for filling missing values.

    Returns:
        pandas.DataFrame: The DataFrame with missing values filled in the specified column.
    """
    df[column_name] = df[column_name].fillna(df[fillna_column_name])
    df.drop(fillna_column_name, axis=1, inplace=True)
    return df

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
    
    # Iterate through each specified column
    for col in columns:
        print(f"Attempting column: {col}")
        # Check if the column can be converted to datetime
        try:
            df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
            print(f"Column {col} transformed successfully.\n")
        except Exception as e:
            print(f"Column {col} is incompatible with datetime: {e}\n")
            # If conversion fails, skip to the next column
            continue
            
    return df_copy





def main():
    # Define the file paths and column patterns
    # Define the directory containing Excel files
    directory = "../data/licenses/"
    # Print the current working directory
    print(f"Current working directory: {os.getcwd()}")
    # Get the directory of the current file
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Define the directory containing Excel files
    directory = os.path.join(current_directory, directory)
    file_paths = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".xlsx")]
    column_patterns = ['ΑΙΤΗΣΗ', 'ΜΗΤΡΩΟ', 'ΗΜΕΡΟΜΗΝΙΑ ΥΠΟΒΟΛΗΣ.*', 'ΕΤΑΙΡΕΙΑ', 'ΗΜΕΡ.*ΕΚΔ.*ΠΑΡΑΓ.*', 'ΗΜΕΡ.*ΛΗΞΗ.*ΠΑΡΑΓ.*', 'ΠΕΡΙΦΕΡΕΙΑ', 'ΠΕΡΙΦΕΡΕΙΑΚΗ ΕΝΟΤΗΤΑ', 'ΔΗΜΟ.* ', 'ΔΗΜΟΤΙΚΗ ΕΝΟΤΗΤΑ', 'ΘΕΣΗ', '.*(MW)', 'ΤΕΧΝΟΛ.*'] 

    # Sort file paths based on their names to process them in order
    file_paths.sort()

    merged_df = merge_dataframes_with_previous_files(file_paths, column_patterns)


# Call the main function
if __name__ == "__main__":
    main()