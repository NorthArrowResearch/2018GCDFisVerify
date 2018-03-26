# Rebecca Rossi - Generate Uncertainty Raster from FIS Error Model Outputs
import os
import time

from osgeo import gdal
import osgeo.osr as osr
from glob import glob
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import pandas as pd


def read_raster(SFM_raster):
    ds = gdal.Open(SFM_raster)
    data = ds.GetRasterBand(1).ReadAsArray()
    data[data == -99] = np.nan
    gt = ds.GetGeoTransform()
    del ds
    return data, gt


def merge_df(slope_data, rough_data):
    df = pd.DataFrame({'slope': slope_data.flatten(), 'rough': rough_data.flatten()})
    return df


def FIS(s, r):
    uncertainty_simulation.input['slope'] = s
    uncertainty_simulation.input['roughness'] = r

    uncertainty_simulation.compute()

    uncert = uncertainty_simulation.output['uncertainty']

    return uncert


def create_raster(data, gt, out_array, outFile):
    cols = data.shape[1]
    rows = data.shape[0]
    out_array[np.isinf(out_array)] = -99
    out_array[out_array > 1000] = -99
    out_array[np.isnan(out_array)] = -99
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(outFile, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform(gt)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(out_array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(26949)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.SetNoDataValue(-99)
    outband.FlushCache()
    outband.ComputeStatistics(False)
    del outband, outRaster


start = time.clock()

slope_rasters = glob(r'F:\analyses\FIS\slope\clipped' + r'\*.tif')
roughness_rasters = glob(r'F:\analyses\FIS\roughness\clipped' + r'\*.tif')
interpolation_error_rasters = glob(r'F:\analyses\FIS\interpolation_error\clipped' + r'\*.tif')

slope = ctrl.Antecedent([0, 3, 6, 16, 24, 30, 45, 62, 74, 90], 'slope')
roughness = ctrl.Antecedent([0, 0.01, 0.02, 0.03, 0.05, 0.1, 0.12, 0.18, 1.0, 2.5], 'roughness')
uncertainty = ctrl.Consequent([0, 0.01, 0.02, 0.04, 0.05, 0.1, 0.2, 0.6, 0.9, 1.2, 1.5, 1.6, 1.9, 2.0], 'uncertainty')

# Generate fuzzy membership functions

# SLOPE
slope['low'] = fuzz.trapmf(slope.universe, [0.0, 0.0, 1.6, 6.0])
slope['moderate'] = fuzz.trapmf(slope.universe, [1.6, 6.0, 9.1, 18.1])
slope['high'] = fuzz.trapmf(slope.universe, [9.1, 18.1, 22.6, 38.6])
slope['extreme'] = fuzz.trapmf(slope.universe, [22.6, 38.6, 90.0, 90.0])

# ROUGHNESS
roughness['low'] = fuzz.trapmf(roughness.universe, [0.000, 0.000, 0.001, 0.006])
roughness['moderate'] = fuzz.trapmf(roughness.universe, [0.001, 0.006, 0.009, 0.020])
roughness['high'] = fuzz.trapmf(roughness.universe, [0.009, 0.020, 0.026, 0.044])
roughness['extreme'] = fuzz.trapmf(roughness.universe, [0.026, 0.044, 2.006, 2.006])

# UNCERTAINTY
uncertainty['low'] = fuzz.trapmf(uncertainty.universe, [0.000, 0.000, 0.009, 0.019])
uncertainty['moderate'] = fuzz.trapmf(uncertainty.universe, [0.009, 0.019, 0.023, 0.046])
uncertainty['high'] = fuzz.trapmf(uncertainty.universe, [0.023, 0.046, 0.072, 0.154])
uncertainty['extreme'] = fuzz.trapmf(uncertainty.universe, [0.072, 0.154, 2.000, 2.000])

# FUZZY RULES

rule1 = ctrl.Rule(slope['low'] & roughness['low'], uncertainty['moderate'])
rule2 = ctrl.Rule(slope['low'] & roughness['moderate'], uncertainty['low'])
rule3 = ctrl.Rule(slope['low'] & roughness['high'], uncertainty['moderate'])
rule4 = ctrl.Rule(slope['low'] & roughness['extreme'], uncertainty['high'])
rule5 = ctrl.Rule(slope['moderate'] & roughness['low'], uncertainty['moderate'])
rule6 = ctrl.Rule(slope['moderate'] & roughness['moderate'], uncertainty['moderate'])
rule7 = ctrl.Rule(slope['moderate'] & roughness['high'], uncertainty['moderate'])
rule8 = ctrl.Rule(slope['moderate'] & roughness['extreme'], uncertainty['high'])
rule9 = ctrl.Rule(slope['high'] & roughness['low'], uncertainty['moderate'])
rule10 = ctrl.Rule(slope['high'] & roughness['moderate'], uncertainty['moderate'])
rule11 = ctrl.Rule(slope['high'] & roughness['high'], uncertainty['high'])
rule12 = ctrl.Rule(slope['high'] & roughness['extreme'], uncertainty['high'])
rule13 = ctrl.Rule(slope['extreme'] & roughness['extreme'], uncertainty['extreme'])
rule14 = ctrl.Rule(slope['extreme'] | roughness['extreme'], uncertainty['high'])

# CONTROL SYSTEM
uncertainty_ctrl = ctrl.ControlSystem(
    [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14])
uncertainty_simulation = ctrl.ControlSystemSimulation(uncertainty_ctrl)

for i in xrange(len(slope_rasters)):

    slope_raster = slope_rasters[i]
    rough_raster = roughness_rasters[i]
    int_err_raster = interpolation_error_rasters[i]

    slope_data, gt = read_raster(slope_raster)
    rough_data, gt = read_raster(rough_raster)
    int_err_data, gt = read_raster(int_err_raster)
    vec3 = int_err_data.flatten().astype('float')

    n = rough_raster.split('\\')[-1].split('.')
    dem_name = n[0] + '.tif'

    vec1 = slope_data.flatten().astype('float')  # flattened array of slope values from a given raster
    vec2 = rough_data.flatten().astype('float')  # flattened array of rougness values
    vec1 = np.round(vec1, 1)
    vec2 = np.round(vec2, 3)

    # pre allocate output array
    uncert = np.zeros(np.shape(vec1)) * np.nan

    # Find index of all finite elements of the array
    ind = np.where(np.isfinite(vec1))[0]

    # classify
    for k in xrange(len(ind)):
        print k
        uncert[ind[k]] = FIS(vec1[ind[k]], vec2[ind[k]])

    new_array = np.maximum(uncert, vec3)

    print 'Now saving raster ...'
    out_array = np.reshape(new_array, np.shape(slope_data))
    outFile = os.path.normpath(os.path.join('F:\\', 'analyses', 'FIS', 'uncertainty', dem_name))
    create_raster(slope_data, gt, out_array, outFile)

    elapsed = (time.clock() - start)
    print "Processing took ", elapsed, "seconds to analyse"

    print "Done!"


