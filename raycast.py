import time
import tkinter as tk
import tkinter.filedialog as fd
from os import path
from tkinter import E, S, W

import geopandas as gp
import matplotlib
import pandas as pd
import shapely


def calculatePercentageInArea(area, points):
    shape = gp.read_file(area)
    ax = shape.plot(color='white', edgecolor='black')
    shapely.speedups.enable()
    percent = 0.00
    for file in points:
        if path.splitext(file)[1] == '.xls' or path.splitext(file)[1] == '.xlsx':
            full_df = pd.read_excel(file, skiprows=2)
        else:
            full_df = pd.read_csv(file, skiprows=2)

        full_df.rename(columns=lambda x: x.strip(), inplace=True)
        filtered_df = full_df.filter(items=['Latitude', 'Longitude', 'IAS'])
        filtered_df.replace(r'^\s*$', 0.0, regex=True, inplace=True)
        filtered_df['IAS'] = filtered_df['IAS'].astype(float)
        flying_df = filtered_df[filtered_df['IAS'] >= 70.0]
        flying_gdf = gp.GeoDataFrame(flying_df, geometry=gp.points_from_xy(
            flying_df.Longitude, flying_df.Latitude))
        flying_gdf.plot(ax=ax, color='red')
        pip_mask = flying_gdf.within(shape.loc[0, 'geometry'])
        result = pip_mask.value_counts()
        pip_data = flying_gdf.loc[pip_mask]
        pip_data.plot(ax=ax, color='blue')
        if result.get(True) is not None:
            percent += ((result.get(True) / len(pip_mask)) * 100.0)
    matplotlib.pyplot.ion()
    matplotlib.pyplot.show()
    return percent / len(points)


class GUI:

    shapeFile = None
    logFiles = None

    def __init__(self, master):
        self.master = master
        master.title("Percentage Usage Inside State")
        master.geometry("500x400")

        self.shapeLabel = tk.Label(
            master, text="Select a GIS shape file (.shp) of the state boundary. Both .shp and .shx files must be in the same directory", wraplength=400, font=[("Courier", 24)])
        self.shapeLabel.pack(pady=10)

        self.shapeButton = tk.Button(
            master, text='Select', command=self.selectShapeFile, font=[("Courier", 24)])
        self.shapeButton.pack(pady=5)

        self.shapeFileLabel = tk.Label(master, text=self.shapeFile)
        self.shapeFileLabel.pack(pady=5)

        self.shapeLabel = tk.Label(
            master, text="Select data files to import", font=[("Courier", 24)])
        self.shapeLabel.pack(pady=10)

        self.shapeButton = tk.Button(
            master, text='Select', command=self.selectLogFiles, font=[("Courier", 24)])
        self.shapeButton.pack(pady=5)

        self.logFileLabel = tk.Label(master, text=self.shapeFile)
        self.logFileLabel.pack(pady=5)

        self.runButton = tk.Button(
            master, text='Run', command=self.do_calculation, font=[("Courier", 24)])
        self.runButton.pack(anchor=S)

        self.resultLabel = tk.Label(
            master, font=[("Courier", 24)], wraplength=400, fg="green4")
        self.resultLabel.pack(pady=5)

    def do_calculation(self):
        start_time = time.process_time()
        result = calculatePercentageInArea(self.shapeFile, self.logFiles)
        end_time = time.process_time()
        self.resultLabel.configure(text="Of the selected files, " + "{:.4f}".format(result) + "% of points were inside " + path.basename(self.shapeFile) +
                                   "\n(Calculated in " + str(end_time-start_time) + " seconds)")

    def selectLogFiles(self):
        self.logFiles = list(fd.askopenfilenames(
            filetypes=[('Excel Workbooks/CSV', ('*.xls', '*.xlsx', '*.csv'))]))
        self.logFileLabel.configure(text='\n'.join(map(str, self.logFiles)))
        self.resultLabel.configure(text="")

    def selectShapeFile(self):
        self.shapeFile = fd.askopenfilename(
            filetypes=[('Shape Files', '*.shp')])
        self.shapeFileLabel.configure(text=self.shapeFile)
        self.resultLabel.configure(text="")


def main():
    root = tk.Tk()
    GUI(root)
    root.mainloop()
