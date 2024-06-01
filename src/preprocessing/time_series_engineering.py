# time_series_engineering.py
import pandas as pd

class ManualSeasonalDecomposition:
    def __init__(self, data: pd.Series, period: int):
        """
        Initialize the ManualSeasonalDecomposition class.

        Parameters:
        - data (pd.Series): The input time series data.
        - period (int): The period of the seasonality (e.g., 12 for monthly data with yearly seasonality).
        """
        self.data = data
        self.period = period

    def moving_average(self, window: int) -> pd.Series:
        """
        Calculate the moving average of the time series.

        Parameters:
        - window (int): The window size for the moving average.

        Returns:
        - pd.Series: The moving average series.
        """
        return self.data.rolling(window=window, center=True).mean()

    def decompose(self) -> dict:
        """
        Perform seasonal decomposition manually.

        Returns:
        - dict: A dictionary containing trend, seasonal, and residual components.
        """
        # Estimate the trend component using a centered moving average
        trend = self.moving_average(window=self.period)
        
        # Detrend the series by subtracting the trend component
        detrended = self.data - trend
        
        # Extract the seasonal component by averaging the detrended values for each period
        seasonal = detrended.groupby(detrended.index.month).transform('mean')
        
        # Calculate the residual component
        residual = self.data - trend - seasonal
        
        return {
            'trend': trend,
            'seasonal': seasonal,
            'residual': residual
        }

class TimeSeriesFeatureEngineering:
    def __init__(self, data: pd.DataFrame, mw_prefix: str = '(MW)', rsi_prefix: str = 'RSI_'):
        """
        Initialize the TimeSeriesFeatureEngineering class.

        Parameters:
        - data (pd.DataFrame): The input dataframe with time series data.
        - mw_prefix (str): The prefix for MW features. Default is 'MW_'.
        - rsi_prefix (str): The prefix for RSI features. Default is 'RSI_'.
        """
        self.data = data
        self.mw_prefix = mw_prefix
        self.rsi_prefix = rsi_prefix

    def calculate_rolling_metrics(self, prefix: str, window_sizes: list = [3, 6, 7, 11, 12, 24]) -> pd.DataFrame:
        """
        Calculate rolling metrics for the features with the given prefix.

        Parameters:
        - prefix (str): The prefix to filter columns.
        - window_sizes (list): List of window sizes for rolling calculations. Default is [3, 6, 12].

        Returns:
        - pd.DataFrame: DataFrame with rolling metrics.
        """
        rolling_metrics = pd.DataFrame(index=self.data.index)
        
        for window_size in window_sizes:
            for feature in self.data.filter(like=prefix).columns:
                rolling_metrics[f'{feature}_mean_rolling_{window_size}'] = self.data[feature].rolling(window=window_size).mean()
                rolling_metrics[f'{feature}_std_rolling_{window_size}'] = self.data[feature].rolling(window=window_size).std()
                rolling_metrics[f'{feature}_min_rolling_{window_size}'] = self.data[feature].rolling(window=window_size).min()
                rolling_metrics[f'{feature}_max_rolling_{window_size}'] = self.data[feature].rolling(window=window_size).max()
                rolling_metrics[f'{feature}_skew_rolling_{window_size}'] = self.data[feature].rolling(window=window_size).skew()
                rolling_metrics[f'{feature}_ewm_{window_size}'] = self.data[feature].ewm(span=window_size).mean()
        
        return rolling_metrics

    def calculate_autocorrelation(self, prefix: str, lags: list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 48]) -> pd.DataFrame:
        """
        Calculate autocorrelation for the features with the given prefix.

        Parameters:
        - prefix (str): The prefix to filter columns.
        - lags (list): List of lag values for autocorrelation calculations. Default is [1, 2, 3].

        Returns:
        - pd.DataFrame: DataFrame with autocorrelation values.
        """
        autocorr = pd.DataFrame(index=self.data.index)
        
        for lag in lags:
            for feature in self.data.filter(like=prefix).columns:
                autocorr[f'{feature}_autocorr_lag_{lag}'] = self.data[feature].autocorr(lag=lag)
        
        return autocorr

    def create_lagged_variables(self, prefix: str, lag_lengths: list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, 46, 58]) -> pd.DataFrame:
        """
        Create lagged variables for the features with the given prefix.

        Parameters:
        - prefix (str): The prefix to filter columns.
        - lag_lengths (list): List of lag lengths to create lagged variables. Default is [1, 2, 3].

        Returns:
        - pd.DataFrame: DataFrame with lagged variables.
        """
        lagged_data = pd.DataFrame(index=self.data.index)
        
        for lag_length in lag_lengths:
            for feature in self.data.filter(like=prefix).columns:
                lagged_data[f'{feature}_lagged_{lag_length}'] = self.data[feature].shift(lag_length)
        
        return lagged_data

    def calculate_seasonal_aggregations(self, prefix: str) -> pd.DataFrame:
        """
        Calculate seasonal aggregations for the features with the given prefix.

        Parameters:
        - prefix (str): The prefix to filter columns.

        Returns:
        - pd.DataFrame: DataFrame with seasonal aggregations.
        """
        seasonal_aggregations = pd.DataFrame(index=self.data.index)
        
        for feature in self.data.filter(like=prefix).columns:
            seasonal_aggregations[f'{feature}_mean_monthly'] = self.data[feature].groupby(self.data.index.month).transform('mean')
        
        return seasonal_aggregations

    def extract_time_based_features(self) -> pd.DataFrame:
        """
        Extract time-based features such as month and year from the index.

        Returns:
        - pd.DataFrame: DataFrame with time-based features.
        """
        time_features = pd.DataFrame(index=self.data.index)
        time_features['month'] = self.data.index.month
        time_features['year'] = self.data.index.year
        return time_features

    def calculate_expanding_metrics(self, prefix: str) -> pd.DataFrame:
        """
        Calculate expanding metrics for the features with the given prefix.

        Parameters:
        - prefix (str): The prefix to filter columns.

        Returns:
        - pd.DataFrame: DataFrame with expanding metrics.
        """
        expanding_metrics = pd.DataFrame(index=self.data.index)
        
        for feature in self.data.filter(like=prefix).columns:
            expanding_metrics[f'{feature}_expanding_mean'] = self.data[feature].expanding().mean()
            expanding_metrics[f'{feature}_expanding_std'] = self.data[feature].expanding().std()
        
        return expanding_metrics

    def calculate_manual_seasonal_decomposition(self, feature: str, period: int) -> pd.DataFrame:
        """
        Manually calculate seasonal decomposition for a specific feature.

        Parameters:
        - feature (str): The feature to decompose.
        - period (int): The period of the seasonality.

        Returns:
        - pd.DataFrame: DataFrame with trend, seasonal, and residual components.
        """
        data = self.data[feature]
        decomposer = ManualSeasonalDecomposition(data, period)
        components = decomposer.decompose()
        
        decomposition = pd.DataFrame(index=self.data.index)
        decomposition[f'{feature}_trend'] = components['trend']
        decomposition[f'{feature}_seasonal'] = components['seasonal']
        decomposition[f'{feature}_residual'] = components['residual']
        
        return decomposition

def run_feature_engineering(data: pd.DataFrame, mw_prefix: str = '(MW)', rsi_prefix: str = 'RSI_') -> pd.DataFrame:
    """
    Run the entire feature engineering process on the given data.

    Parameters:
    - data (pd.DataFrame): The input dataframe with time series data.
    - mw_prefix (str): The prefix for MW features. Default is '(MW)'.
    - rsi_prefix (str): The prefix for RSI features. Default is 'RSI_'.

    Returns:
    - pd.DataFrame: DataFrame with engineered features.
    """
    engineer = TimeSeriesFeatureEngineering(data, mw_prefix, rsi_prefix)

    # Perform seasonal decomposition for MW features
    decomposition_mw = engineer.calculate_manual_seasonal_decomposition(f'{mw_prefix}_sum', period=12)

    engineer.data = pd.concat([data, decomposition_mw], axis=1)

    # Calculate autocorrelation for MW features
    autocorr_mw = engineer.calculate_autocorrelation(engineer.mw_prefix)

    # Calculate seasonal aggregations for MW features
    seasonal_aggregations_mw = engineer.calculate_seasonal_aggregations(engineer.mw_prefix)

    # Calculate expanding metrics for MW features
    expanding_metrics_mw = engineer.calculate_expanding_metrics(engineer.mw_prefix)

    # Calculate rolling metrics for MW features
    rolling_metrics_mw = engineer.calculate_rolling_metrics(engineer.mw_prefix)

    engineer.data = pd.concat([data, decomposition_mw, autocorr_mw, seasonal_aggregations_mw, expanding_metrics_mw, rolling_metrics_mw], axis=1)

    # Create lagged variables for MW features
    lagged_data_mw = engineer.create_lagged_variables(engineer.mw_prefix)

    # Repeat the process for RSI features
    autocorr_rsi = engineer.calculate_autocorrelation(engineer.rsi_prefix)
    seasonal_aggregations_rsi = engineer.calculate_seasonal_aggregations(engineer.rsi_prefix)
    expanding_metrics_rsi = engineer.calculate_expanding_metrics(engineer.rsi_prefix)
    rolling_metrics_rsi = engineer.calculate_rolling_metrics(engineer.rsi_prefix)
    lagged_data_rsi = engineer.create_lagged_variables(engineer.rsi_prefix)

    # Extract time-based features
    time_features = engineer.extract_time_based_features()

    # Concatenate all the results into a single DataFrame
    final_result = pd.concat([
        rolling_metrics_mw, autocorr_mw, lagged_data_mw, seasonal_aggregations_mw, expanding_metrics_mw,
        rolling_metrics_rsi, autocorr_rsi, lagged_data_rsi, seasonal_aggregations_rsi, expanding_metrics_rsi,
        time_features
    ], axis=1)

    extended_result = pd.concat([data, decomposition_mw, final_result], axis=1)

    return final_result, extended_result
