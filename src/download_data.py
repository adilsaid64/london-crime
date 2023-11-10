import pandas as pd
import time


def download_data_from_web():  
    '''
    Download latest historical and crime datasets from web.
    '''
    historical_df = pd.read_csv('https://data.london.gov.uk/download/recorded_crime_summary/bf244ffa-326b-49cc-a7df-0e3193abe818/MPS%20LSOA%20Level%20Crime%20%28Historical%29.csv')
    recent_df = pd.read_csv('https://data.london.gov.uk/download/recorded_crime_summary/221142dd-f7b2-4209-921e-4de833a82285/MPS%20LSOA%20Level%20Crime%20%28most%20recent%2024%20months%29.csv')

    return historical_df, recent_df


def save_data(df:pd.DataFrame, file_name:str, save_directory:str):
    '''
    After downloading latest dataset, this functions saves the dataset into local storage
    '''
    
    df.to_csv(f'{save_directory}/{file_name}.csv', index=False)


def download_and_save_data():
    '''
    Downloads and saves the data.

    Helper functions: save_data() and download_data_from_web()
    '''
    
    request_time = time.strftime('%Y-%m-%d--%H-%M')

    historical_df, recent_df = download_data_from_web()

    save_data(df=historical_df, file_name=f'losa-historical--{request_time}', save_directory='data')
    save_data(df=recent_df, file_name=f'lsoa-recent--{request_time}', save_directory='data')