# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 20:32:44 2017

@author: DARLINGTON MENSAH
"""
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import ClsKriging as kg
import ClsSemivariogram as sv
import time
from scipy.spatial import cKDTree as KDTree


class Main:
    """
    Main class for performing the kriging and surface mass balance
    with the necessary data.
    """

    def __init__(self):
        """
        Instantiation of the class and initialisation of class variables
        """
        self._kg = kg
        self._sv = sv

    def openfile(self):
        """
        Function for obtaining a data file path
        Returns a string of file path
        """
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilenames(parent=root, title='Choose a file')
        return filepath

    def importfile(self, filepath):
        """
        Function for importing data file. Removes point less than 10cm from
        previous points. 
        Returns:
            Array of prediction data (x,y)
        """
        data = self._read_input_files(filepath)
        t = KDTree(data)
        mask = np.ones(data.shape[:1], bool)
        idx = 0
        nxt = 1
        while nxt:
            mask[t.query_ball_point(data[idx], 0.1)] = False
            nxt = mask[idx:].argmax()
            mask[idx] = True
            idx += nxt
        return data[mask]

    def importfile1(self, filepath):
        """
        Function for importing data file. Removes point less than 10cm from
        previous points. 
        Returns:
            Array of prediction data (x,y)
        """
        data = self._read_input_files(filepath)
        return data

    @staticmethod
    def _read_input_files(filepath):
        """Read kriging inputs from Excel or whitespace-delimited text.

        The first three columns must be X, Y and value. Text files may have
        either no header (the Estacas .dat output) or a single non-numeric
        header line, which is skipped automatically.
        """
        frames = []
        for file in filepath:
            filename = str(file).lower()
            if filename.endswith((".dat", ".txt", ".csv")):
                try:
                    values = np.loadtxt(file, comments="#", delimiter=None)
                except ValueError:
                    values = np.loadtxt(file, comments="#", delimiter=None, skiprows=1)
                values = np.asarray(values, dtype=float)
                if values.ndim == 1:
                    values = values.reshape(1, -1)
                if values.shape[1] < 3:
                    raise ValueError(f"{file} must contain at least three columns: X Y value")
                frames.append(values[:, :3])
            else:
                df = pd.read_excel(file).iloc[:, :3]
                frames.append(df.apply(pd.to_numeric, errors="coerce").to_numpy())

        if not frames:
            return np.empty((0, 3), dtype=float)
        data = np.vstack(frames)
        return data[~np.isnan(data).any(axis=1)].astype(float)

    def krige(self, semi_filepath, krige_filepath, prediction_filepath, nug):
        """
        Function that returns the kriged data for the study data
        INPUT:
            semi_filepath = filepath for the data used in obtaining the semivariogram
            krige_filepath = filepath of experimental data for performing kriging
            prediction_filepath = filepath of grid data of where kriging will be performed.
        OUTPUT:
            File containing the predicted value of each grid coordenates obtained from the kriging operation
        EXTRA INFO:
            If data to be used for obtaining the semivariogram is the same experimental data,
            then semi_filepath = krige_filepath
        """       
        var_param = self._sv.Semivariogram(semi_filepath).isotropy(nug) 
        input("Press Enter to continue...")
        return self._kg.Kriging().ordinary(var_param, krige_filepath, prediction_filepath)

    def ordinary_Krige(self, semi_filepath, krige_filepath, prediction_filepath):
       return self.krige(self.importfile(semi_filepath), self.importfile(krige_filepath), self.importfile1(prediction_filepath), 0.1)

# pylint: disable=C0103
start_time = time.time()
main = Main()

interpolate = main.ordinary_Krige(main.openfile(), main.openfile(), main.openfile())
print("---- %s seconds----" % (time.time() - start_time))
sample = pd.DataFrame(interpolate)
save_as_name = filedialog.asksaveasfilename()
# Always write a plain-text result usable by Elmer/Unix tools.  Excel output
# remains available when xlsxwriter is installed, for visual inspection.
sample.to_csv(save_as_name + '.dat', sep='\t', index=False, header=False)
try:
    writer = pd.ExcelWriter(save_as_name + '.xlsx', engine='xlsxwriter')
    sample.to_excel(writer, sheet_name='Kriging', index=False)
    writer.close()
except ImportError:
    print('xlsxwriter is not installed; only the .dat result was written.')
