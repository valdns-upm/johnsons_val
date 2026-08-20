# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 21:00:45 2017

@author: Darlington Mensah
"""
import numpy as np


class Model:
    """
    Covariance function model class containing functions for fitting the experimental variogram
    """

    def __init__(self):
        pass

    @staticmethod
    def stable(setlag, setnugget, setsill, setrange, setalpha):
        """
        Stable/Natural covariance function
        Parameters include:
            setlag: a array of the lag of the data
            setnugget: a constant of the nugget value of the data
            setsill: a constant of the sill/variance of the data
            setrange: a constant of the range of the data
            setalpha: a constant which defines the power value (between 1 and 2)
        """   
        return setnugget + setsill*(1-np.exp(-3*(np.array(setlag)/setrange)**setalpha))

    @staticmethod
    def gaussian(setlag, setnugget, setsill, setrange, setalpha=1):
        """
        Gaussian covariance function
        Parameters include:
            setlag: a array of the lag of the data
            setnugget: a constant of the nugget value of the data
            setsill: a constant of the sill/variance of the data
            setrange: a constant of the range of the data
            setalpha: a constant which defines the power value (between 1 and 2)
        """
        del setalpha
        return setnugget + setsill*(1-np.exp(-3*(np.array(setlag)/setrange)**2))

    @staticmethod
    def spherical(setlag, setnugget, setsill, setrange, setalpha=1):
        """
        Spherical covariance function
        Parameters include:
            setlag: a array of the lag of the data
            setnugget: a constant of the nugget value of the data
            setsill: a constant of the sill/variance of the data
            setrange: a constant of the range of the data
            setalpha: a constant which defines the power value (between 1 and 2)
        """
        del setalpha
        return setnugget + setsill*((1.5*(np.array(setlag)/setrange)-
                                     0.5*(np.array(setlag)/setrange)**3))

    @staticmethod
    def exponential(setlag, setnugget, setsill, setrange, setalpha=1):
        """
        Exponential covariance function
        Parameters include:
            setlag: a array of the lag of the data
            setnugget: a constant of the nugget value of the data
            setsill: a constant of the sill/variance of the data
            setrange: a constant of the range of the data
            setalpha: a constant which defines the power value (between 1 and 2)
        """
        del setalpha
        return setnugget + setsill*(1-np.exp(-3*(np.array(setlag)/setrange)))

    @staticmethod
    def fitfunction(x, a, b, c, d):
        """
        3º Polynomial function for fitting mean and StD funcion via least square fit
        """
        return a * x**3 + b * x**2 + c * x + d