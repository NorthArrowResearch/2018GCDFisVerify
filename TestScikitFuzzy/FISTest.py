import numpy as np
import skfuzzy as fuzz
import pandas as pd
import csv
from fisImporter import FisModel

# First load our Data
data_ugr = pd.read_csv(r"../CSV/CHaMP_UGR_CRBW05583-013882_2013.csv")
data_feshie = pd.read_csv(r"../CSV/FeshieInputs.csv")

# Now load our FISFiles
Test1 = FisModel("../FisFiles/Test1.fis")
CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr = FisModel("../FisFiles/CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr.fis")
CHaMP_TS_ZError_PD_SLPdeg_IntErr = FisModel("../FisFiles/CHaMP_TS_ZError_PD_SLPdeg_IntErr.fis")
CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr = FisModel("../FisFiles/CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr.fis")
GPS_ZError_PD_SLPdeg_PQ = FisModel("../FisFiles/GPS_ZError_PD_SLPdeg_PQ.fis")
TS_ZError_PD_SLPdeg = FisModel("../FisFiles/TS_ZError_PD_SLPdeg.fis")


print "-------------------\nFeshie TS_ZError_PD_SLPdeg"
for idx, row in data_feshie[['SlopeDeg', 'PointDensity']].iterrows():
    result = TS_ZError_PD_SLPdeg.compute(dict(row))
    print result

print "-------------------\nFeshie GPS_ZError_PD_SLPdeg_PQ"
for idx, row in data_feshie[['SlopeDeg', 'PointDensity', '3DPointQuality']].iterrows():
    result = GPS_ZError_PD_SLPdeg_PQ.compute(dict(row))
    print result

print "-------------------\nUGR CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr"
for idx, row in data_ugr[['Slope', 'PointDensity', '3DPointQuality', 'InterpolationError']].iterrows():
    result = CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr.compute(dict(row))
    print result

print "-------------------\nUGR CHaMP_TS_ZError_PD_SLPdeg_IntErr"
for idx, row in data_ugr[['Slope', 'PointDensity', 'InterpolationError']].iterrows():
    result = CHaMP_TS_ZError_PD_SLPdeg_IntErr.compute(dict(row))
    print result

print "-------------------\nUGR CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr"
for idx, row in data_ugr[['Slope', 'PointDensity', 'Roughness', '3DPointQuality', 'InterpolationError']].iterrows():
    result = CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr.compute(dict(row))
    print result

def graphMe():
    # https://stackoverflow.com/questions/14404962/how-could-i-arrange-multiple-pyplot-figures-in-a-kind-of-layout
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    n = 4  # n = number of inputs
    gs = gridspec.GridSpec(4, n)

    # subplot(nrows, ncols, index, **kwargs)

    plt.subplot(4, 1, 1)

def mfPlot():
    print "hi there"