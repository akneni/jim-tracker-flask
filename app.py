from flask import Flask, request, render_template, Response
import pymongo
from datetime import datetime
import os
import matplotlib.pyplot as plt
import io
from plotdep import *
import operator

app = Flask(__name__, static_folder='static', template_folder='templates')

# Connect to MongoDB
AUTH_TOKEN = os.environ['AUTH_TOKEN']
client = pymongo.MongoClient(AUTH_TOKEN)
jim_tracker_db = client.get_database('jim-tracker')



# Global Vars ( sorts them in alphabetical order)
list_exercises = list(jim_tracker_db.get_collection('workouts').find())
list_exercises = sorted(list_exercises, key=operator.itemgetter('Name'))
list_exercises = [''] + list_exercises
list_names = list(jim_tracker_db.get_collection('names').find())
list_names = sorted(list_names, key=operator.itemgetter('name'))
list_names = [''] + list_names

@app.route('/')
@app.route('/home')
@app.route('/root')
def home():
    return render_template('home.html')

@app.route('/add-entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        name = request.form['name']
        exercise = request.form['exercise']
        weight = request.form['weight']
        reps = request.form['reps']

        if (name == '' or exercise == ''):
            return render_template('add-entry.html', list_exercises=list_exercises, list_names=list_names, display_err="true")

        log_entry(name, exercise, weight, reps)
    

    

    return render_template('add-entry.html', list_exercises=list_exercises, list_names=list_names)

@app.route('/see-raw', methods=['GET', 'POST'])
def see_raw():
    if request.method == 'POST':
        name = request.form['name']
        exercise = request.form['exercise']
        
        if exercise.strip() == "":
            res = jim_tracker_db.get_collection('logs').find({'name':name})
        else:
            res = jim_tracker_db.get_collection('logs').find({'name':name, 'exercise':exercise})
            
        return render_template("raw-displayed.html", raw_data = list(res))


    return render_template("see-raw.html", list_names=list_names, list_exercises=list_exercises)

@app.route('/plot-progress', methods=['GET', 'POST'])
def plot_progress():
    if request.method == 'POST':
        name = request.form['name']
        exercise = request.form['exercise']
        max_rep = float(request.form['max']) if str(request.form['max']) != '' else -1
        min_rep = float(request.form['min']) if str(request.form['min']) != '' else -1
        
        # Call the display_progress function
        display_progress(name, exercise, max_rep, min_rep, jim_tracker_db)
        
        # Generate the plot and return it as a response
        output = io.BytesIO()
        plt.savefig(output, format='png')
        output.seek(0)
        return Response(output.read(), mimetype='image/png')

    return render_template('plot-progress.html', list_exercises=list_exercises, list_names=list_names)


# Function to log entry
# Similar to your log_entry function
def log_entry(name, exercise, weight, reps):
    new = {
        'name':name,
        'date':datetime.now().strftime('%m-%d-%Y'),
        'exercise':exercise,
        'weight':float(weight),
        'reps':float(reps)
    }

    jim_tracker_db.get_collection('logs').insert_one(new)


if __name__ == '__main__':
    app.run(debug=True)
