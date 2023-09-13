from flask import Flask, request, render_template, Response
import pymongo
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import io

def display_progress(name, exercise, max_rep, min_rep, jim_tracker_db):
    res = jim_tracker_db.get_collection('logs').find({'name':name, 'exercise':exercise})
    df = pd.DataFrame(list(res))
    try:
        del df['_id']
    except KeyError:
        pass


    if max_rep > 0:
        df = df[df['reps'] <= max_rep]
    if min_rep > 0:
        df = df[df['reps'] >= min_rep]
    

    x_vals = pd.to_datetime(df["date"])

    plt.style.use('dark_background')

    res = jim_tracker_db.get_collection('workouts').find()
    wk_df = pd.DataFrame(list(res))
    try:
        del wk_df['_id']
    except KeyError:
        pass

    if wk_df[wk_df['Name'] == exercise]['Category'].iloc[0] == 'weighted':
        plt.title(exercise)
        plt.xlabel("Timespan")
        plt.ylabel("Weight")
        plt.plot(x_vals, df['weight'])
    elif wk_df[wk_df['Name'] == exercise]['Category'].iloc[0] == 'unweighted':
        # if see_progress_rep_max.strip() != "":
        #     st.warning("Rep Rage Field is only for weighted excersises")
        #     return
        plt.title(exercise)
        plt.xlabel("Timespan")
        plt.ylabel("Reps")
        plt.plot(x_vals, df['reps'])
    elif wk_df[wk_df['Name'] == exercise]['Category'].iloc[0] == 'timed':
        # if see_progress_rep_max.strip() != "":
        #     st.warning("Rep Rage Field is only for weighted excersises")
        #     return
        plt.title(exercise)
        plt.xlabel("Timespan")
        plt.ylabel("Seconds")
        plt.plot(x_vals, df['reps'])
    
    locator = mdates.AutoDateLocator()
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=4))

    return plt