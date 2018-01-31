import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

def get_average_channel(df,chan,start_time):
    """ Get the average value of a specific channel by turbine and by case if available
    inputs
    df: data frame from reading in sowfa outputs
    chan: which channel to average
    start_time: time to start averaging

    outputs:
    df_out: df out averages, and if available by case"""

    # If case is available include in average
    if 'case' in df.columns:
        df_out = df[['case','turbine',chan]].groupby(['case','turbine']).mean().reset_index()

    # Otherwise just by turbine
    else:
        df_out = df[['turbine',chan]].groupby(['turbine']).mean().reset_index()

    return df_out

def get_total_frame(df):
    """ Take a frame with turbine column and sum across them to get totals
    inputs:
    df, sowfa input dataframe

    outputs:
    df_total: totaled frame"""



    # If case is available include in average
    if 'case' in df.columns:
        df_total = df.groupby(['time', 'case']).sum().reset_index()
    else:
        df_total = df.groupby(['time']).sum().reset_index()

    # If eliminate period and turbine from the columns
    if 'period' in df_total.columns:
        columns = [c for c in df_total.columns if ((c != 'period') and (c != 'turbine'))]
        df_total = df_total[columns]

    

    return df_total


def compare_power(df,period=100.,ax=None,power_channel='powerGenerator',relative=False):
    """ Construct a plot which compares the power output between cases
    inputs:
    df, sowfa input dataframe, should have case column

    outputs:
    ax, the figure"""

    # If no ax, make one
    if not ax:
        fig, ax = plt.subplots()

    # Work out the number of turbines
    num_turbines = len(df.turbine.unique())

    # Make a power df
    df_power = df[['case','turbine','time',power_channel]]

    # Get the mean power and append it
    df_mean = get_total_frame(df_power)
    df_mean[power_channel] = df_mean[power_channel]/num_turbines
    df_mean['turbine'] = 'total'

    # Merge it in
    df_power = df_power.append(df_mean)

    # # Add a period column
    # df_power['period'] = df_power.time/100
    # df_power['period'] = df_power.period.astype(int)

    # Merge down the periods
    df_power = df_power[['time','turbine','case',power_channel]]
    # df_power = df_power.groupby(['period','turbine','case']).agg([np.mean,np.std])#.agg(np.mean,np.SHIFT_UNDERFLOW)
    # df_power.columns=['mean','std']
    # df_power = df_power.reset_index()
    # print(df_power)

    # If wanting the relative value
    if relative:

        # Assume the baseline has either base or Base in it
        base_column = [c for c in df_power.case.unique() if (('base' in c) or ('Base' in c))][0]

        # Get a list of cases that aren't the bases
        cases = [c for c in df_power.case.unique() if c != base_column]

        # Spin out the power
        df_power = df_power.set_index(['time','turbine','case']).unstack()
        
        # Rename the baseline column
        df_power = df_power.rename(index=str,columns={base_column:'baseline'})
        
        # Flatten columns
        df_power.columns =df_power.columns.get_level_values(1)



        # Now for all the cases, convert to percent change
        for c in cases:
            df_power[c] = 100. * (df_power[c] - df_power['baseline'])/df_power['baseline']

        # Drop the baseline
        df_power = df_power[cases]

        # Reset the index
        df_power = df_power.reset_index()

        # Melt the cases
        df_power = pd.melt(df_power,id_vars=['time','turbine'],var_name='case',value_name=power_channel)

        # print(df_power)
        
    # Plot it
    ax = sns.barplot(data=df_power,x='turbine',y=power_channel,hue='case',ax=ax)

    # Print the mean values
    print(df_power.groupby(['case','turbine']).median())

    # Plot it
    # ax = sns.boxplot(data=df_power,x='turbine',y=power_channel,hue='case',ax=ax)
    
    

    return ax