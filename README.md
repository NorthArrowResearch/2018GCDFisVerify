# FIS Value Tester

This repo is a response to:

https://github.com/Riverscapes/gcd/issues/190

This file references a google spreadsheet with all the values:

<https://docs.google.com/spreadsheets/d/1v6abeYaKZXQAyN25VEuN3NvffOTFth0cl1cJ24zNfLE/edit#gid=1355638424>

This file uses Jupyter notebook (or it will when I get around to it)

```
jupyter notebook
```



## Suggested Standard for Unit Testing FISgs

Lets treat the GCD 6 FIS outputs as 'truth' as we'd previously verified those against [Matlab Fuzzy Logic Toolbox](https://www.mathworks.com/products/fuzzy-logic.html?s_tid=srchtitle) (see also #174). I would strongly suggest we also test against [scikit](https://pypi.python.org/pypi/scikit-fuzzy), and as that is open-source and Python it should be a quick an easy test to shove the text files through it.  

I think the method we used above is good for testing. Briefly:
1. Have a point shapefile with 15-30 points manually selected to represent the diversity and range of values in the input file (e.g. [These for Feshie](https://usu.box.com/s/9t3u9wnh2ub0d41bnxgda01zzqij2v80)). See [video](https://youtu.be/3VrUBEV5kTs?t=3m47s)
2. Then produce all FIS associated surfaces required for *.fis model in both GCD 6.1.14 and GCD 7.0.8.
3.  Use the ESRI `Extract Multi Values to Points` geoprocessing tool to extract all inputs and outputs for both GCD 6 and GCD 7 into same spreadsheet (see [here](https://youtu.be/3VrUBEV5kTs?t=8m5s) if confused).
4. Compare results (NOTE: I did notice a small difference in the significant digits saved on the point density calculation between GCD 6 & GCD 7... so we should also keep an eye out on comparing the inputs). However, it may make sense to (if the inputs are slightly different derived from each version of GCD 6, to do the comparison of FIS outputs using *exactly* the same inputs in both. 
5. We should set some tolerance for acceptable differences in outputs (i.e. rounding error)
## Suggested Datasets, FIS Models & Why
1. Feshie 2006 (from Tutorial [n-running-an-fis-dem-error-model](http://gcd6help.joewheaton.org/tutorials--how-to/workshop-tutorials/n-running-an-fis-dem-error-model)) using this FIS [TS_ZError_PD_SLPdeg.fis](https://github.com/Riverscapes/fis-dem-error/blob/master/BySurveyType/TS/TS_ZError_PD_SLPdeg.fis) - Uses slope (degrees) & point density. Based on [Wheaton et al. (2010)](https://www.researchgate.net/publication/227747150_Accounting_for_uncertainty_in_DEMs_from_repeat_topographic_surveys_Improved_sediment_budgets). * Use this because this is what we use in tutorials and teach off of.*
2. Feshie 2006 with [GPS_ZError_PD_SLPdeg_PQ.fis](https://github.com/Riverscapes/fis-dem-error/blob/master/BySurveyType/GPS/GPS_ZError_PD_SLPdeg_PQ.fis) - Uses slope (degrees), GPS 3D Point Quality & point density. Based on [Wheaton et al. (2010)](https://www.researchgate.net/publication/227747150_Accounting_for_uncertainty_in_DEMs_from_repeat_topographic_surveys_Improved_sediment_budgets). * Use this because this is what we use in tutorials was published.*
3.  CHaMP UGR_CRBW05583-013882 2013 Visit from  tutorial [o-champ-fis-error-modelling](http://gcd6help.joewheaton.org/tutorials--how-to/workshop-tutorials/o-champ-fis-error-modelling) - with three different FIS models all from [Bangen et al. 2016 WRR Paper](https://www.researchgate.net/publication/292210478_Error_modeling_of_DEMs_from_topographic_surveys_of_rivers_using_fuzzy_inference_systems):
  - [CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr.fis](https://github.com/Riverscapes/fis-dem-error/blob/master/CHaMP/2014/CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr.fis) - i.e. 4 Input
  - [CHaMP_TS_ZError_PD_SLPdeg_IntErr.fis](https://github.com/Riverscapes/fis-dem-error/blob/master/CHaMP/2014/CHaMP_TS_ZError_PD_SLPdeg_IntErr.fis) - i.e. 3 Input
  - [CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr.fis](https://github.com/Riverscapes/fis-dem-error/blob/master/CHaMP/2014/CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr.fis)

This will give us five solid tests from published and peer-reviewed FIS and known datasets we use in tutorials to compare against.  We can also ask @bangen if she has any suggestions.


