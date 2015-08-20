#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Go through each model, vary one parameter and fit it back to the
default value of that model.
"""
from __future__ import division, print_function
import sys
from os.path import abspath, dirname, split

import matplotlib.pylab as plt
import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))

import pycorrfit
from pycorrfit.fcs_data_set import Correlation, Fit


# GLOBAL PARAMETERS FOR THIS TEST:
TAUMIN = 1e-3
TAUMAX = 1e6
TAULEN = 100
FITALG = "Lev-Mar"


def fit_single_parameter(modelid, fullparms, parmid, parmval, noise=False):
    """
    Use the full parameter set `fullparms` and leave a single parameter
    `parmid` variable during the fit.
    Returns the fitted value of the parameter with index `parmid`
    """
    corr = Correlation(fit_model=modelid, fit_algorithm=FITALG, verbose=0)
    tau = np.exp(np.linspace(np.log(TAUMIN),np.log(TAUMAX), TAULEN))
    # Create artificial data by using the current fit_model
    data = corr.fit_model(fullparms, tau)
    if noise:
        if noise is True:
            deltanoise = (np.max(data)-np.min(data))/20
        else:
            deltanoise = (np.max(data)-np.min(data))*noise
        anoise = (np.random.random(data.shape[0])-.5)*deltanoise
        data += anoise
    # Add artificial data to data set
    corr.correlation = np.dstack((tau, data))[0]
    # Set variable parameters
    fit_bool = np.zeros(fullparms.shape[0])
    fit_bool[parmid] = True
    corr.fit_parameters_variable = fit_bool
    fullparms_edit = fullparms.copy()
    fullparms_edit[parmid] = parmval
    corr.fit_parameters = fullparms_edit
    Fit(corr)
    return corr.fit_parameters[parmid]


def deviate_parameter(model, parmid):
    """
    Returns a deviated version of the parameter with id `parmid`.
    Performs model checks to ensure the new value is physical.
    """
    val = model.default_values[parmid]
    if val==0:
        val+=.1
    else:
        val*=.9
    return val


def test_fit_single_parameter():
    """
    Deviate a single parameter and fit it back.
    """
    faillist=list()
    for model in pycorrfit.models.models:
        fullparms = model.default_values
        for ii, val in enumerate(fullparms):
            newval = deviate_parameter(model, ii)
            fitval = fit_single_parameter(model.id, fullparms, ii, newval, noise=False)
            #print(val-fitval)
            if not np.allclose([val], [fitval]):
                faillist.append([model.id, model.parameters[0][ii], val, fitval])
    if len(faillist) != 0:
        raise ValueError("Model tests failed for:\n", faillist)


def fit_single_parameter_with_noise(noise=0.005):
    """
    Deviate a single parameter and fit it back.
    """
    faillist=list()
    for model in pycorrfit.models.models:
        fullparms = model.default_values
        for ii, val in enumerate(fullparms):
            newval = deviate_parameter(model, ii)
            fitval = fit_single_parameter(model.id, fullparms, ii, newval, noise=noise)
            if not np.allclose([val], [fitval], atol=.1, rtol=.1):
                faillist.append([model.id, model.parameters[0][ii], val, fitval])
    return faillist


def test_fit_single_parameter_with_noise_one_permille():
    faillist = fit_single_parameter_with_noise(noise=0.001)
    if len(faillist) > 1:
        raise ValueError("Model tests failed for:\n", faillist)

def test_fit_single_parameter_with_noise_two_percent():
    faillist = fit_single_parameter_with_noise(noise=0.02)
    if len(faillist) > 5:
        raise ValueError("Model tests failed for:\n", faillist)

def test_fit_single_parameter_with_noise_five_percent():
    faillist = fit_single_parameter_with_noise(noise=0.05)
    if len(faillist) > 10:
        raise ValueError("Model tests failed for:\n", faillist)
        




if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
