import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

def display_progress(name, exercise, max_rep, min_rep, jim_tracker_db):
    res = jim_tracker_db.get_collection('logs').find({'name':name, 'exercise':exercise})
    df = pd.DataFrame(list(res))
    try:
        del df['_id']
    except KeyError:
        pass

    try:
        if max_rep > 0:
            df = df[df['reps'] <= max_rep]
        if min_rep > 0:
            df = df[df['reps'] >= min_rep]
    except Exception as err:
        print("\n"*4 + str(err) + "\n"*4)
    
    # get the largest value in each day
    try:
        dates = df['date'].unique()
        weight = df[['date', 'weight']].groupby("date").max()['weight'].to_numpy()
        placeholder = pd.DataFrame({
            "date":dates,
            "weight":weight
        })
        df = placeholder
    except Exception as err:
        print("\n"*4 + str(err) + "\n"*4)

    try:
        if len(df['date']) == 0:
            return False
    except KeyError:
        return False

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
        plt.plot(x_vals, df['weight'], marker='v')  # Add marker='v' here
    elif wk_df[wk_df['Name'] == exercise]['Category'].iloc[0] == 'unweighted':
        plt.title(exercise)
        plt.xlabel("Timespan")
        plt.ylabel("Reps")
        plt.plot(x_vals, df['reps'], marker='v')  # Add marker='v' here
    elif wk_df[wk_df['Name'] == exercise]['Category'].iloc[0] == 'timed':
        plt.title(exercise)
        plt.xlabel("Timespan")
        plt.ylabel("Seconds")
        plt.plot(x_vals, df['reps'], marker='v')  # Add marker='v' here
    
    
    locator = mdates.AutoDateLocator()
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=4))

    return True