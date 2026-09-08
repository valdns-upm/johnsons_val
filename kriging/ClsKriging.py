# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 16:21:48 2017

@author: DARLINGTON MENSAH
"""
import numpy as np
from scipy.spatial.distance import pdist, squareform


class Kriging:
    """
    Class for calculating the semivariogram
    Input:
        1. Filepath of experimental data to be kriged
        2. Filepath of prediction grid data on which kriging would be performed
    """

    def __init__(self):
        """
        Instantiation of the class
        """        
        pass

    def ordinary(self, var_param, data, gdata):
        """
        Function for prediction unknown values at several points.
        Uses the Ordinary kriging method
        Retuns:
            Arrray of prediction point (x,y,z)
        """
        nrow, dummy_cols = data.shape
        gnrow, dummy_cols = gdata.shape
        prediction = []
        N = 1000
        if nrow < 1000:               
            for i, dummy_val in enumerate(gdata):
#                for i in range(14327, len(gdata)):
                # distance between u and each data point in P
                d = np.sqrt((data[:, 0]-gdata[i, 0])**2.0 + (data[:, 1]-gdata[i, 1])**2.0)
                # add these distances to P
                P = np.vstack((data.T, d)).T
                # sort P by these distances
                # take the first N of them
                P = P[d.argsort()]
             
                # apply the covariance model to the distances
                k = (var_param[0] + var_param[1]*(1-np.exp(-3*(P[:,3]/var_param[2])**var_param[3])))
                # cast as a matrix
                k = np.matrix(k).T
             
                # form a matrix of distances between existing data points
                K1 = squareform(pdist(P[:,:2]))
                # apply the covariance model to these distances
                K = (var_param[0] + var_param[1]*(1-np.exp(-3*(K1.ravel()/var_param[2])**var_param[3])))
                # re-cast as a NumPy array -- thanks M.L.                    
                K = np.array(K)
                # reshape into an array
                K = K.reshape(len(P), len(P))
                K[K1 == 0] = 0
                # cast as a matrix
                K = np.matrix(K)

                # add a column and row of ones to Ks,
                # with a zero in the bottom, right hand corner
                K2 = np.matrix(np.ones((len(P)+1, len(P)+1)))
                K2[:len(P), :len(P)] = K
                K2[-1, -1] = 0.0
            
                # add a one to the end of ks
                k3 = np.matrix(np.ones((len(P)+1, 1)))
                k3[:len(P)] = k
             
                # calculate the kriging weights
#                    weights = np.linalg.inv(K2) * k3
                weights = np.linalg.lstsq(K2, k3, rcond = 1)
                weights = weights[:-3][0][:-1]
                weights = np.array(weights)
             
                # calculate the residuals
                residuals = P[:, 2]
                print(str(i) + ' of ' + str(len(gdata)))
                # calculate the estimation
                prediction.append(np.dot(weights.T, residuals))
            # The third grid column is only a placeholder.  Elmer velocity
            # observations require exactly X, Y and the kriged value.
            return np.hstack((gdata[:, :2], prediction))
        else:
            for i, dummy_val in enumerate(gdata):
                # distance between u and each data point in P
                d = np.sqrt((data[:, 0]-gdata[i, 0])**2.0 + (data[:, 1]-gdata[i, 1])**2.0)
                # add these distances to P
                P = np.vstack((data.T, d)).T
                # sort P by these distances
                # take the first N of them
                P = P[d.argsort()[:N]]

                # apply the covariance model to the distances
                k = (var_param[0] + var_param[1]*(1-np.exp(-3*(P[:,3]/var_param[2])**var_param[3])))
                # cast as a matrix
                k = np.matrix(k).T
             
                # form a matrix of distances between existing data points
                K1 = squareform(pdist(P[:,:2]))
                # apply the covariance model to these distances
                K = (var_param[0] + var_param[1]*(1-np.exp(-3*(K1.ravel()/var_param[2])**var_param[3])))
                # re-cast as a NumPy array -- thanks M.L.                    
                K = np.array(K)
                # reshape into an array
                K = K.reshape(N, N)
                K[K1 == 0] = 0
                # cast as a matrix
                K = np.matrix(K)

                # add a column and row of ones to Ks,
                # with a zero in the bottom, right hand corner
                K2 = np.matrix(np.ones((N+1, N+1)))
                K2[:N, :N] = K
                K2[-1, -1] = 0.0
            
                # add a one to the end of ks
                k3 = np.matrix(np.ones((N+1, 1)))
                k3[:N] = k

                weights = np.linalg.lstsq(K2, k3, rcond = 1)
                weights = weights[:-3][0][:-1]
                weights = np.array(weights)
             
                # calculate the residuals
                residuals = P[:, 2]
                print(str(i) + ' of ' + str(len(gdata)))
                # calculate the estimation
                prediction.append(np.dot(weights.T, residuals))
            return np.hstack((gdata[:, :2], prediction))
