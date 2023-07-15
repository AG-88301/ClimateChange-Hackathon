# Import Data
import pandas as pd
import json

import matplotlib
matplotlib.use("TkAgg")

# Plot Data
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from numpy import int64
from multiprocessing.pool import ThreadPool

from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Initialise vars
plt.rcParams["figure.figsize"] = [15, 7] 
plt.rcParams["figure.autolayout"] = True

VARIABLE = "co2"

# Cloropleth key
CO2_KEY = {1: 0.1, 50: 0.175, 100: 0.25, 1000: 0.5, 2000: 0.75}
POPULATION_KEY = {1000000: 0.1, 5000000: 0.2, 10000000: 0.25, 50000000: 0.3, 100000000: 0.5, 500000000: 0.6, 1000000000: 0.8}
KEYS = {"co2": CO2_KEY, "population": POPULATION_KEY}
drop2key = {"Carbon Dioxide Levels":"co2", "Population": "population"}


# Load all data
@staticmethod
def loadData() -> None:
    global DATA, COUNTRIES, DF

    DF = pd.read_csv('owid-co2-data.csv') # import climate change data

    with open('countries.geojson') as f:
        DATA = json.load(f) # import country border data

    COUNTRIES = [] # country names
    for country in DATA["features"]:
        country = country["properties"]['ADMIN']
        COUNTRIES.append(country)

# plot inputted country on map
def plotOnMap(country: str) -> None:
    try:
        ind, conc = COUNTRIES.index(country), float(DF.loc[(DF['country']==country) & (int64(DF['year']) == YEAR)][VARIABLE]) # country geometry found?
    except:
            return

    key = KEYS[VARIABLE]
    key_key = list(key.keys())
    if conc > key_key[-1]:
        conc = 1
    for k in key_key[::-1]:
        if conc > k:
            conc = key[k]
    if conc > 1: conc = 0

    if DATA["features"][ind]["geometry"]["type"] == "Polygon": # One island country
        shape = Polygon(DATA["features"][ind]["geometry"]["coordinates"][0])
        plotShape(shape, conc)
    else: # Multi-island country
        for shape in DATA["features"][ind]["geometry"]["coordinates"]:
            plotShape(Polygon(shape[0]), conc)

# Helper function for plotOnMap()
def plotShape(shape: Polygon, conc: float) -> None:
    try:
        x, y = shape.exterior.xy
        plt.fill(x, y, color=(conc, 0.07, 0.03)) # fill colour currently random (rgb)
        plt.plot(x, y, c="black")
    except:
        print(conc)

loadData()

def update():
    global YEAR
    global VARIABLE

    YEAR = slider.get()
    VARIABLE = drop2key[clicked.get()]

    plt.clf()
    # for country in COUNTRIES:
    #     plotOnMap(country)
    with ThreadPool() as pool:
        pool.map(plotOnMap, COUNTRIES)
    canvas.draw()

root = Tk()


# Year Slider
slider = Scale(root, from_=1851, to=2021, orient=HORIZONTAL)
slider.pack()

# Choose Variable to plot
options = ["Carbon Dioxide Levels", "Population"]
clicked = StringVar()
clicked.set("Carbon Dioxide Levels")
drop = OptionMenu(root, clicked, *options)
drop.pack()

# Update map
updateButton = Button(root, text="Update Map", command=update)
updateButton.pack()

# Map canvas to integrate matplotlib
figure = plt.gcf()
canvas = FigureCanvasTkAgg(figure=figure, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# Toolbar for map
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack()

# Add data to map
figure.canvas.draw_idle()
update()

root.mainloop()

# plt.show()
