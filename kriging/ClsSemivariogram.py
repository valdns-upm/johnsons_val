# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 21:08:22 2017

@author: DARLINGTON MENSAH
"""
import pandas as pd
import numpy as np
from pylab import plt
from scipy.optimize import curve_fit
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.spatial.distance import pdist, squareform
from ClsModel import Model as fnc
#import time


class Semivariogram:
    """
    Class for calculating the semivariogram
    """

    def __init__(self, getdata):
        """
        Instantiation of the class and initialisation of class variables
        """
        self._getdata = getdata

    def isotropy(self, nug):
        """
        Computes and fits a covariance model to the experimental data. Assumes
        ISOTROPY
        Input:
            array of data coordinate (x,y,z)
        Output:
            square-from of pairwise distance
        """
        data = self._getdata
        pwdist = squareform(pdist(data[:, :2]))
        pwresi = (data[:, 2, None] - data[:, 2]) ** 2
        vecdistance = pwdist.ravel()
        vecresidual = pwresi.ravel()
        uniquedistance = np.unique(vecdistance)
        classdistance = np.searchsorted(uniquedistance, vecdistance)
        summation = np.bincount(classdistance, weights=vecresidual)
        gamma = summation / (2 * np.bincount(classdistance))

        frequency = []
        semivariance = []
        npoint = 20
        max_lag = int(np.ceil(np.max(pwdist)))
        firstlag = max_lag / 100
        lags = np.hstack((0, np.linspace(firstlag, max_lag, npoint)))

        count = -1
        for lag in lags[:-1]:
            count = count+1
            frequency.append(np.sum((uniquedistance[:] >= lag)&(uniquedistance[:] < lags[count+1])))
            semivariance.append(np.sum(gamma[(uniquedistance[:] >= lag)&(uniquedistance[:] < lags[count+1])])/
                np.sum((uniquedistance[:] >= lag)&(uniquedistance[:] < lags[count+1])))
        semivariance = np.array(semivariance, dtype=float)

#        weight = np.sqrt(semivariance) ** 2

        xlags = (lags[1:] + lags[:-1]) / 2
        sill = np.var(data[:, 2])
        nugget = nug ** 2
        silltofit = sill - nugget

        if np.isnan(semivariance).any():
            index = np.argwhere(np.isnan(semivariance))
            semivariance = np.delete(semivariance, index)
            xlags = np.delete(xlags, index)
#            weight = np.delete(weight, index)

        if np.any(semivariance == 0):
            index = np.argwhere(np.any(semivariance == 0))
            semivariance = np.delete(semivariance, index)
            xlags = np.delete(xlags, index)
#            weight = np.delete(weight, index)

        #: Variable values obtained from minimum least square algorithm
        variogram_param, dummy_mat = curve_fit(fnc.stable, xlags, semivariance, absolute_sigma=True,
                                     bounds=([nugget-0.1, silltofit-0.1, (max_lag*0.001), 1.01],
                                             [nugget, silltofit, max_lag, 1.99]))

#        variogram_param, dummy_mat = curve_fit(fnc.stable, xlags, semivariance, sigma=weight, absolute_sigma=True,
#                                     bounds=([nugget-0.1, silltofit-0.1, (max_lag*0.001), 1.01],
#                                             [nugget, silltofit, max_lag, 1.99]))

        classes = np.linspace(1, npoint, npoint)
        freq_series = pd.Series(frequency)
        plt.figure(figsize=(12, 8))
        ax = freq_series.plot(kind='bar')
        ax.set_title("Data population")
        ax.set_xlabel("Nº of Lag")
        ax.set_ylabel("Nº points per Lag")
        plt.text(0.6*plt.xlim()[1], 0.9*plt.ylim()[1], 'Total = '+str(np.sum(frequency)), fontsize=11)
        ax.set_xticklabels(classes)
        rects = ax.patches
        for rect in rects: # For each bar: Place a label
            y_value = rect.get_height() # Get X and Y placement of label from rect
            x_value = rect.get_x() + rect.get_width() / 2
            space = 5 # Number of points between bar and label. Change to your liking.
            va = 'bottom' # Vertical alignment for positive values
            if y_value < 0: # If value of bar is negative: Place label below bar
                space *= -1 # Invert space to place label below
                va = 'top' # Vertically align label at top
            label = "{:.1f}".format(y_value) # Use Y value as label and format number with one decimal place

            # Create annotation
            plt.annotate(
                label,                      # Use `label` as label
                (x_value, y_value),         # Place label at end of the bar
                xytext=(0, space),          # Vertically shift label by `space`
                textcoords="offset points", # Interpret `xytext` as offset in points
                ha='center',                # Horizontally center label
                va=va)                      # Vertically align label differently for
                                            # positive and negative values.

#        plt.savefig(str(time.localtime()[0]) + str(time.localtime()[1]) + str(time.localtime()[2])+'_' + 
#                    str(time.localtime()[3]) + str(time.localtime()[4]) + str(time.localtime()[5]) + 
#                    '_Histogram.png', fmt='png', dpi=200)
        plt.show()

        #: Semivariance value for the theoretical fit
        curvefit = fnc.stable(xlags, nugget, silltofit, variogram_param[2], variogram_param[3])
        s = InterpolatedUnivariateSpline(xlags, curvefit, ext=0)
        new_xlags = np.hstack((0, xlags))
        new_semivariance = s(new_xlags)
        if new_semivariance[0] <= 0:
            new_semivariance[0] = semivariance[0]

        plt.plot(xlags, semivariance, 'x', new_xlags, new_semivariance, 'r-')
        plt.text(plt.xlim()[0], 0.95*plt.ylim()[1], ' Mean = '+str(np.round(np.mean(data[:, 2]), decimals=2)), fontsize=10)
        plt.text(plt.xlim()[0], 0.9*plt.ylim()[1], ' Nugget = '+str(nugget), fontsize=10)
        plt.text(plt.xlim()[0], 0.85*plt.ylim()[1], ' Sill = '+str(np.round(sill, decimals=2)), fontsize=10)
        plt.text(plt.xlim()[0], 0.8*plt.ylim()[1], ' Range = '+str(np.round(variogram_param[2])), fontsize=10)
        plt.text(plt.xlim()[0], 0.75*plt.ylim()[1], ' Alpha = '+str(np.round(variogram_param[3], decimals=2)), fontsize=10)
        plt.xlabel('Lag [m]')
        plt.ylabel('Semivariance')
        plt.title('Semivariogram Fit')
#        plt.savefig(str(time.localtime()[0]) + str(time.localtime()[1]) + str(time.localtime()[2])+'_' + 
#                    str(time.localtime()[3]) + str(time.localtime()[4]) + str(time.localtime()[5]) 
#                    + '_Semivariogram.png', fmt='png', dpi=200)
        plt.show()
        variogram_param[0] = nugget # new_semivariance[0]
        variogram_param[1] = sill
        return variogram_param
