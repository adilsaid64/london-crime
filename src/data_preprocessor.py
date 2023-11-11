import os
import pandas as pd
from glob import glob

from src.logger_setup import setup_logger

# logger object for the current module
logger = setup_logger(__name__)

def load_data(file_type : str) -> pd.DataFrame:
    '''
    Will get data from a data folder in the directory.

    :params file_type (str): 'recent' or 'historical'.

    :returns df (pd.DataFrame): Latest file_type dataframe inside the data folder.
    '''
    
    # Define the path pattern for the CSV files
    path_pattern = f"data/*{file_type}*.csv"
    
    # List all matching files
    files = glob(path_pattern)
    
    # Check if files are found
    if not files:
        raise ValueError(f"No files found for type '{file_type}'")
    
    # Get the latest file by creation time
    latest_file = max(files, key=os.path.getctime)
    logger.info(f"Loading the latest {file_type} file: {latest_file}")

    # Load and return the DataFrame
    return pd.read_csv(latest_file)


def merge_crime_data(recent_df : pd.DataFrame, historical_df : pd.DataFrame) -> pd.DataFrame:
    '''
    Merges recent and historical crime data.
    '''
    return pd.merge(historical_df, recent_df, on=['LSOA Code', 'LSOA Name', 'Borough', 'Major Category', 'Minor Category'], how='outer')


def aggregate_to_yearly(merged_df:pd.DataFrame) -> pd.DataFrame:

    yearly_df = merged_df.fillna(0).copy()

    # Loop through unique years present in the dataset
    years = {col[:4] for col in yearly_df.columns if col.isdigit()}

    for year in years:
        # List columns for that year
        monthly_columns = [col for col in yearly_df.columns if col.startswith(year)]
        
        # Sum the monthly columns and create a new yearly column
        yearly_df[year] = yearly_df[monthly_columns].sum(axis=1)
        
        yearly_df.drop(monthly_columns, axis=1, inplace=True)

    return yearly_df

def filter_data(df: pd.DataFrame, column: str = 'Major Category', category_filters: list = ['Theft', 'Burglary']) -> pd.DataFrame:
    '''
    Filters a DataFrame based on values in a specified column.

    :param df (pd.DataFrame): The DataFrame to filter.
    :param column (str): The column name to apply the filter on.
    :param category_filters (list): A list of values to filter the column by. If None, no filtering is applied.

    :return (pd.DataFrame): A filtered DataFrame if filter values are provided; otherwise, the original DataFrame.
    '''

    if category_filters is None:
        logger.error('No filter value provided. Please choose a filter.')
        return df

    if column not in df.columns:
        logger.error(f'Column "{column}" not in dataframe.')
        return df

    filtered_df = df[df[column].isin(category_filters)]
    return filtered_df


def load_and_process_data() -> pd.DataFrame:
    recent_df = load_data('recent')
    historical_df =load_data('historical')
    merged_df = merge_crime_data(recent_df, historical_df)

    return merged_df