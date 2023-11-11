from src.data_preprocessor import load_and_process_data, aggregate_to_yearly, filter_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import plotly.express as px

from src.logger_setup import setup_logger

# logger object for the current module
logger = setup_logger(__name__)

# ---- Functions that prepare data for timeseries analysis ---- #

def group_by(df: pd.DataFrame, columns : list = ['Borough'], agg_func :str ='sum', sort : bool =False) -> pd.DataFrame:
    '''
    Groups a DataFrame by specified column(s) and applies an aggregation function.

    :params df (pd.DataFrame): The DataFrame to group.
    :params columns (str or list): The column(s) to group by.
    :params agg_func (str or dict, optional): The aggregation function(s) to apply. Default is 'sum'.
    :params sort (bool, optional): Whether to sort the grouped data. Default is False.

    :returns pd.DataFrame: The grouped DataFrame.

    # Example Usage
    df = load_and_process_data()
    group_by(df, columns = ['Borough', 'Major Category'])
    '''

    # Ensure columns is a list for consistency
    if isinstance(columns, str):
        columns = [columns]

    # Check if all columns are in DataFrame
    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        logger.error(f'Column(s) {", ".join(missing_columns)} not found in dataset')
        return None

    grouped_df = df.groupby(by=columns).agg(agg_func)

    if sort:
        grouped_df = grouped_df.sort_values(by=columns)

    return grouped_df

def get_time_series(df, columns : list = ['Borough', 'Major Category'], agg_func : str = 'sum', crimes : list = ['Theft'], yearly : bool = False):
    '''
    # Example Usage
    crimes = ['Violence Against the Person']
    monthly = get_time_series(df = df, crimes = crimes, yearly=False)
    yearly = get_time_series(df = df, crimes = crimes, yearly=True)
    '''

    grouped_by_borough = group_by(df = df, columns = columns, agg_func=agg_func, sort = True)
    yearly_by_borough = aggregate_to_yearly(grouped_by_borough).sort_index(axis = 1)

    # Filtered data by borough and by crime
    filted_data = filter_data(df = grouped_by_borough.reset_index() if yearly == False else yearly_by_borough.reset_index(),
                               column='Major Category', category_filters = crimes).reset_index(drop = True)
    yearly_data_sums = filted_data.drop(columns = ['Borough', 'Major Category']).sum()

    return yearly_data_sums.sort_index()

def prep_data_for_monthly_heat_maps(df, crimes):
    '''
    # Example useage
    crimes = ['Violence Against the Person']
    monthly_pivot = prep_data_for_monthly_heat_maps(df, crimes)
    '''
        
    monthly_totals = get_time_series(df, columns=['Borough', 'Major Category'], crimes=crimes, yearly = False)
    monthly_totals = pd.DataFrame(monthly_totals).reset_index()
    monthly_totals['Year'] = monthly_totals['index'].str[:4]
    monthly_totals['Month'] = monthly_totals['index'].str[4:] 
    monthly_pivot = monthly_totals.pivot("Month", "Year", 0)

    return monthly_pivot


# ---- Static plots ---- #

def static_line_plot(data, crimes):
    '''
    # Example usage
    static_line_plot(data = monthly, crimes=crimes)
    static_line_plot(data = yearly, crimes=crimes)
    '''
    plt.figure(figsize=(15, 6))
    sns.lineplot(x=data.index, y=data.values, marker="o", color="b")
    plt.title(f'Yearly Trend of {", ".join(str(crime) for crime in crimes)} Crimes in London (2010-2023)', fontsize=15)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Total Crime Counts', fontsize=12)
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.show()

def static_plot_monthly_heatmaps(monthly_pivot, crimes):
    '''
    # Example useage
    crimes = ['Violence Against the Person']
    monthly_pivot = prep_data_for_monthly_heat_maps(df, crimes)
    static_plot_monthly_heatmaps(monthly_pivot=monthly_pivot, crimes=crimes)
    '''
    plt.figure(figsize=(15, 8))
    sns.heatmap(monthly_pivot, cmap="YlGnBu", linewidths=.5)
    plt.title(f'Monthly Distribution of {", ".join(str(crime) for crime in crimes)} Crimes in London (2010-2023)', fontsize=15)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Month', fontsize=12)
    plt.tight_layout()
    plt.show()

# ---- Interactive plots ---- #

def interactive_line_plot(data, crimes):
    '''
    # Example usage
    yearly = get_time_series(df = df, crimes = crimes, yearly=True)
    interactive_line_plot(data = yearly, crimes = crimes)
    '''


    fig = px.line(data, x=data.index.values, y=data.values,
                markers=True, title=f'Yearly Trend of {", ".join(str(crime) for crime in crimes)} Crimes in London (2010-2023)',
                labels={'x': 'Year', 'y': 'Total Crime Counts'})

    fig.update_layout(xaxis_title='Year',
                    yaxis_title='Total Crime Counts',
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightPink'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightBlue'),
                    plot_bgcolor='white')

    fig.show()


def interactive_monthly_heat_map(monthly_pivot, crimes):
    '''
    # Example usage
    crimes = ['Violence Against the Person']
    monthly_pivot = prep_data_for_monthly_heat_maps(df, crimes)
    interactive_monthly_heat_map(monthly_pivot=monthly_pivot, crimes = crimes)
    '''
    
    fig = px.imshow(monthly_pivot,
                    labels=dict(x="Year", y="Month", color="Total Crime Counts"),
                    x=monthly_pivot.columns,
                    y=monthly_pivot.index,
                    title=f'Monthly Distribution of {", ".join(str(crime) for crime in crimes)} Crimes in London (2010-2023)',
                    color_continuous_scale='YlGnBu')  # Yellow to Green to Blue color scale

    fig.update_xaxes(side="bottom")
    fig.update_layout(
        xaxis_nticks=36,
        width=1000,  # Set the width of the figure
        height=800   # Set the height of the figure
    )
    fig.show()