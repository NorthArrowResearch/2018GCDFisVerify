import pandas as pd
import re
from fisImporter import FisModel
import numpy as np

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


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value


def graphMe(fismodel, title):
    # https://stackoverflow.com/questions/14404962/how-could-i-arrange-multiple-pyplot-figures-in-a-kind-of-layout
    import matplotlib.pyplot as plt

    simid = fismodel.sim.unique_id

    colors = ["#0082c8", "#3cb44b", "#f58231", "#911eb4", "#46f0f0", "#d2f53c"]

    SMALL_SIZE = 6
    MEDIUM_SIZE = 8
    BIGGER_SIZE = 10

    plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
    plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    num_ants = len(fismodel.antecedents)
    num_conseqs = len(fismodel.consequents)

    rows = num_ants + num_conseqs
    cols = 1

    plt.figure(num=None, figsize=(6, 8), dpi=300, facecolor='w', edgecolor='k')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=None)



    rowcounter = 0
    for antlabel, ant in fismodel.antecedents.iteritems():

        # A line of zeros is convenient
        ax = plt.subplot2grid((rows, cols), (rowcounter, 0))
        ax.axvline(x=ant.input._sim_data[simid], color='k', label="v: {:.2f}".format(ant.input._sim_data[simid]), linewidth=1.0, linestyle='dashed')
        ax.set_title("ANTECEDENT {}".format(antlabel))

        # Create some useful objects to graph against

        c = 0 # color counter
        for mflabel, mf in ant.terms.iteritems():
            val = mf.membership_value._sim_data[simid]
            mfarr = mf.mf
            legendlabel = "{}: {:.2f}".format(mflabel, val)
            ax.plot(ant.universe, mf.mf, label=legendlabel, color=colors[c], linewidth=1.0)
            if val > 0:
                zeros = np.zeros_like(ant.universe, dtype=np.float64)
                vals = np.full_like(ant.universe, val)

                ax.fill_between(ant.universe, zeros, mfarr, where=mfarr>zeros, facecolor=colors[c], alpha=0.5, interpolate=True)
                ax.fill_between(ant.universe, vals, mfarr, where=mfarr > zeros, facecolor='w', alpha=1,
                                interpolate=True)
            c += 1

        ax.legend(framealpha=0.5)
        rowcounter += 1

    # Now let's render the defuzzifier in the spare space.


    # We assume there's only ever one output
    conseqlabel = ""
    for conseqlabel, cons in fismodel.consequents.iteritems():
        defuzz = fismodel.sim.output[conseqlabel]
        ax = plt.subplot2grid((rows, cols), (rowcounter, 0), colspan=cols)
        ax.axvline(x=defuzz, color='k', label="defuzz: {:.2f}".format(defuzz), linewidth=1.0, linestyle='dashed')
        ax.set_title("CONSEQUENT {}".format(conseqlabel))

        c = 0 # color counter
        for mflabel, mf in cons.terms.iteritems():
            mfarr = mf.mf
            val = mf.membership_value._sim_data[simid]
            legendlabel = "{}: {:.2f}".format(mflabel, val)
            ax.plot(cons.universe, mfarr, label=legendlabel, color=colors[c], linewidth=1.0)

            if val > 0:
                zeros = np.zeros_like(cons.universe, dtype=np.float64)
                vals = np.full_like(cons.universe, val)
                ax.fill_between(cons.universe, zeros, mfarr, where=mfarr>zeros, facecolor=colors[c], alpha=0.5, interpolate=True)
                ax.fill_between(cons.universe, vals, mfarr, where=mfarr > zeros, facecolor='w', alpha=1,
                                interpolate=True)
            c += 1

        ax.legend(framealpha=0.5)
        rowcounter += 1

    plt.suptitle("{}\n Centroid Defuzz: {}".format(title, fismodel.sim.output[conseqlabel]))
    plt.savefig('./imgs/{}.png'.format(slugify(title)))
    # plt.show()
    print ""






print "-------------------\nFeshie TS_ZError_PD_SLPdeg"
for idx, row in data_feshie[['SlopeDeg', 'PointDensity']].iterrows():
    result = TS_ZError_PD_SLPdeg.compute(dict(row))
    graphMe(TS_ZError_PD_SLPdeg, "Feshie TS_ZError_PD_SLPdeg CELL: {}".format(idx+1))
    print result

print "-------------------\nFeshie GPS_ZError_PD_SLPdeg_PQ"
for idx, row in data_feshie[['SlopeDeg', 'PointDensity', '3DPointQuality']].iterrows():
    result = GPS_ZError_PD_SLPdeg_PQ.compute(dict(row))
    graphMe(TS_ZError_PD_SLPdeg, "Feshie GPS_ZError_PD_SLPdeg_PQ CELL: {}".format(idx+1))
    print result

print "-------------------\nUGR CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr"
for idx, row in data_ugr[['Slope', 'PointDensity', '3DPointQuality', 'InterpolationError']].iterrows():
    result = CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr.compute(dict(row))
    graphMe(TS_ZError_PD_SLPdeg, "UGR CHaMP_TS_ZError_PD_SLPdeg_3DQ_IntErr CELL: {}".format(idx + 1))
    print result

print "-------------------\nUGR CHaMP_TS_ZError_PD_SLPdeg_IntErr"
for idx, row in data_ugr[['Slope', 'PointDensity', 'InterpolationError']].iterrows():
    result = CHaMP_TS_ZError_PD_SLPdeg_IntErr.compute(dict(row))
    graphMe(TS_ZError_PD_SLPdeg, "UGR CHaMP_TS_ZError_PD_SLPdeg_IntErr CELL: {}".format(idx + 1))
    print result

print "-------------------\nUGR CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr"
for idx, row in data_ugr[['Slope', 'PointDensity', 'Roughness', '3DPointQuality', 'InterpolationError']].iterrows():
    result = CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr.compute(dict(row))
    graphMe(TS_ZError_PD_SLPdeg, "UGR CHaMP_TS_ZError_PD_SLPdeg_SR_3DQ_IntErr CELL: {}".format(idx + 1))
    print result
