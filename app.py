from flask import Flask, render_template, send_file, request
import time
import pandas as pd
import plotly.express as px


app = Flask(__name__)

links = {
    "Home": "/",
    "View Raw Data": "/view_data",
    "Descriptive statistics": "/view_statistics",
    "Plotting graphs": "/plots",
    "Comparison": "/compare",
    "Download dataset": "/download"
}

season = {
    "01": "Winter",
    "02": "Winter",
    "03": "Spring",
    "04": "Spring",
    "05": "Spring",
    "06": "Summer",
    "07": "Summer",
    "08": "Summer",
    "09": "Autumn",
    "10": "Autumn",
    "11": "Autumn",
    "12": "Winter"
}


def render_index(html_intro=None, image=None, html_plot=None, html_string=None, html_table=None, filters=None, current_filter_value="", plot_filter=None, html_li=None):
    return render_template("index.html", links=links, image=image, code=time.time(), html_string=html_string, html_intro=html_intro,
                           html_table=html_table, filters=filters, current_filter_value=current_filter_value, plot_filter=plot_filter, html_li=html_li)


def statistics(data, column):
    return [column.lower().replace('_', ' '), {'mean': data[column].mean(), 'median': data[column].median(), 'standard deviation': data[column].std()}]


def seasons(data, column, season):
    d = {}
    for row in range(len(data["month"])):
        d[season.get(data["month"][row][3:5])] = d.get(season.get(data["month"][row][3:5]), 0) + data[column][row]
    return d

@app.route('/', methods=['GET'])
def main_page():
    text=['DSBA 211-1', 'Student: Stepan Chizhov', 'Dataset: Crimes in Russia between 2003-2020']
    return render_index(html_intro=text)


@app.route(links["Download dataset"], methods=['GET'])
def download_data():
    return send_file("data/crime.csv", as_attachment=True)


@app.route(links["View Raw Data"], methods=['GET', 'POST'])
def view_data():
    df = pd.read_csv("data/crime.csv")
    html_string = df.to_html()
    return render_index(html_string=html_string)


@app.route(links["Descriptive statistics"], methods=['GET', 'POST'])
def view_statistic():
    df = pd.read_csv("data/crime.csv")
    errors = []
    values = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.getlist('filters')
        current_filter_value = current_filter
        if current_filter:
            for name in current_filter:
                values.append(statistics(df, name))
            
    return render_index(html_table=values, filters=["Choose columns for statistics:", list(pd.read_csv("data/crime.csv").columns)], current_filter_value=current_filter_value)


@app.route(links["Plotting graphs"], methods=['GET', 'POST'])
def plots():
    df = pd.read_csv("data/crime.csv")
    errors = []
    number_of_crimes = []
    if request.method == "POST":
        current_filter = request.form.getlist('filters')
        if current_filter:
            try:
                for col in current_filter:
                    number_of_crimes.append(col)
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    if number_of_crimes != []:
        plot = px.line(df, x='month', y=number_of_crimes)
        return render_index(html_string=plot.to_html(full_html=False, include_plotlyjs='cdn'), filters=["Choose columns for plot:", list(pd.read_csv("data/crime.csv").columns)])
    return render_index(filters=["Choose columns for plot:", list(pd.read_csv("data/crime.csv").columns)])


@app.route(links["Comparison"], methods=['GET'])
def compare():
    df = pd.read_csv("data/crime.csv")
    veh_theft = pd.DataFrame.from_dict(seasons(df, "Vehicle_theft", season), orient='index')
    plot1, plot2 = px.bar(veh_theft, color=veh_theft.index, title='Vehicle theft per seasons'), px.line(df, x='month', y=["Murder", "Weapons"], title="Murder and Weapon comparison")
    text_1 = "From the bar chart we can see that most of vehicle thefts were committed during warm seasons and least during cold seasons. Indeed, weather conditions effects because  some of cars that could be parked on private warm parkings or vehicle cannot start due to cold weather. Also, it is harder to drive when it is icy weather and it can cause unexpected consequences for theft. However, there are winter holidays that can be a reason for low statistic of vehicle thefts in winter owing to less quantity of police officers who are working during these days."
    text_2 = "From line graph it can be seen that in 2003 there was dramatically fell in weapon usage but  murders reacted on this later and less sharply only in 2006 it began to decrease slightly. The reason for this can be that murder crimes need investigation process which can last for a long time. From 2004 until 2006 murders and weapon crimes are at the same level, but we cannot say that all murders were committed with weapons usage due to  murder crimes reactions. After 2006 murders and weapon usage became independent of each other."

    return render_index(html_string=plot1.to_html(full_html=False, include_plotlyjs='cdn') + text_1 + plot2.to_html(full_html=False, include_plotlyjs='cdn') + text_2)


app.run()
