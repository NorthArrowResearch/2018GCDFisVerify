import numpy as np
import skfuzzy as fuzz
import csv
from fisImporter import FisModel

# First load our Data
data_ugr_1 = [row for row in csv.DictReader(open("./CSV/CHaMP_UGR_CRBW05583-013882_2013_CHaMPTSZErrorPDSLPdeg3DQIntErr.csv"))]
data_ugr_2 = [row for row in csv.DictReader(open("./CSV/CHaMP_UGR_CRBW05583-013882_2013_CHaMPTSZErrorPDSLPdegIntErr.csv"))]
data_ugr_3 = [row for row in csv.DictReader(open("./CSV/CHaMP_UGR_CRBW05583-013882_2013_CHaMPTSZErrorPDSLPdegSR3DQIntErr.csv"))]
data_feshie_gps = [row for row in csv.DictReader(open("./CSV/FeshieGPSZErrorPDSLPdegPQ.csv"))]
data_feshie_tsz = [row for row in csv.DictReader(open("./CSV/FeshieTSZErrorPDSLPdeg.csv"))]

# Now load our FISFiles
CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr = FisModel("./FisFiles/CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr.fis")
CHaMP_TS_ZError_PD_SLPdeg_IntErr = FisModel("./FisFiles/CHaMP_TS_ZError_PD_SLPdeg_IntErr.fis")
CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr = FisModel("./FisFiles/CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr.fis")
GPS_ZError_PD_SLPdeg_PQ = FisModel("./FisFiles/GPS_ZError_PD_SLPdeg_PQ.fis")
TS_ZError_PD_SLPdeg = FisModel("./FisFiles/TS_ZError_PD_SLPdeg.fis")

print "hi"

