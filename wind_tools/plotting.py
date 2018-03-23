"""plotting module
"""

# import sys
# import os
# import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats
# import imp

def data_plot(df,x,y,color='b',label='_nolegend_',x_bins=None,ax=None):

    df_sub = df[[x,y]]

    if x_bins is None:
        x_bins = np.sort(df_sub[x].astype(int).unique()).astype(float)
    bin_width = x_bins[1] - x_bins[0]
    x_edge = np.arange(x_bins[0]-bin_width/2.0,x_bins[-1]+bin_width/2.0 + bin_width,bin_width)

    if not ax:
        fig, ax = plt.subplots()


    # Add and remove the binned column
    df_sub['bin_val'] = pd.cut(df_sub[x], bins=x_edge,labels=x_bins,right=True)

    # Get some stats
    df_stat = df_sub[[y,'bin_val']].groupby(['bin_val']).agg([np.mean,np.std,lambda x: scipy.stats.sem(x, ddof=1) * 1.96])#   [[.groupby()
    df_stat.columns = ['mean_val','std_val','ci']# df_stat.columns.droplevel()
    df_stat = df_stat.reset_index()
    df_stat['bin_val'] = df_stat.bin_val.astype(float)

    # Plot the underlying points
    ax.scatter(df_sub[x],df_sub[y],color=color,label='_nolegend_',alpha=0.01,s=0.5,marker='.')

    # Plot the main trend
    # print(df_stat.bin_val)
    ax.plot(df_stat.bin_val,df_stat.mean_val,label=label,color=color)
    ax.fill_between(df_stat.bin_val,df_stat.mean_val-df_stat.std_val,df_stat.mean_val+df_stat.std_val,alpha=0.2,color=color,label='_nolegend_')

    # print(df_stat.head())


    

    