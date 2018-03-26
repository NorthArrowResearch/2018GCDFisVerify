import numpy as np
import math
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import re

class FisModel:

    def __init__(self, filename):

        self.rules = []

        self.antecedents = {}
        self.consequents = {}

        self.fisdict = {
            "System": {},
            "Input": {},
            "Output": {},
            "Rules": []
        }

        # Populate the dictionary with raw values from the .fis file
        self.parsefisfile(filename)

        # Now build all the antecedeants
        for idx, input in self.fisdict["Input"].iteritems():
            # Create the sparsest universe possible from the integers
            ant = ctrl.Antecedent(self._createuniverse(input["MemberFunctions"]), input["Name"])
            for mf in input["MemberFunctions"].itervalues():
                func = self._getshapefunc(mf["func"])
                ant[mf["label"]] = func(ant.universe, mf["points"])
            self.antecedents[input["Name"]] = ant

        # Now build up the consequent(s)
        for idx, input in self.fisdict["Output"].iteritems():
            cons = ctrl.Consequent(self._createuniverse(input["MemberFunctions"]), input["Name"])
            for mf in input["MemberFunctions"].itervalues():
                func = self._getshapefunc(mf["func"])
                cons[mf["label"]] = func(cons.universe, mf["points"])
            self.consequents[input["Name"]] = cons

        # Build our ruleset from the array in the text file
        self.rules = [self._buildrule(ruledict) for ruledict in self.fisdict["Rules"]]

        # For debug purposes print out an english representation of our rules:
        for r in self.rules:
            print(str(r) + '\n')

        # Now build us a simulation we can use
        self.system = ctrl.ControlSystem(self.rules)
        self.sim = ctrl.ControlSystemSimulation(self.system)

    def compute(self, inputs):
        self.sim.inputs(inputs)
        self.sim.compute()
        return self.sim.output

    def _createuniverse(self, mfdict):
        """
        A universe is just the specification of every value that could exist in our set.

        For now we just create an ordered list of all the vertices in our

        TODO: Might want to try just using the endpoints to see if that speeds up performance

        :param mfdict:
        :return:
        """
        universe = [pt for mfpts in mfdict.itervalues() for pt in mfpts["points"]]
        # remove duplicates
        universe = list(set(universe))
        # sort
        universe.sort()
        return universe

    def _buildrule(self, ruledict):
        """
        This could probably be done by a couple of one-liners but I'm breaking it out so it's easier to check

        :return:
        """

        # This is where any NOT operators get applied
        ants = None
        consqs = None

        def maybeornot(ant_cons, ruleind):
            return ~ant_cons[ruleind[0]][ruleind[1]] if ruleind[2] is True \
                else ant_cons[ruleind[0]][ruleind[1]]

        for ruleant in ruledict['antecedents']:
            if ants is None:
                ants = maybeornot(self.antecedents, ruleant)
            else:
                if ruledict['logic'] == "AND":
                    ants = ants & maybeornot(self.antecedents, ruleant)
                else:
                    ants = ants | maybeornot(self.antecedents, ruleant)

        for rulecons in ruledict['consequents']:
            if consqs is None:
                consqs = maybeornot(self.consequents, rulecons)
            else:
                if ruledict['logic'] == "AND":
                    consqs = consqs & maybeornot(self.consequents, rulecons)
                else:
                    consqs = consqs | maybeornot(self.consequents, rulecons)

        return ctrl.Rule(ants, consqs)


    def parsefisfile(self, filename):
        """
        Parse the text .fis file line-by-line

        :param filename:
        :return:
        """
        SECTREGEX = "^\[([a-zA-Z]+)([\d]*)\]"

        lines = [line.strip() for line in open(filename, 'r')]

        currsection = ""
        curritem = None

        for line in [iterline for iterline in lines if len(iterline) > 0]:
            if re.match(SECTREGEX, line):
                thematch = re.search(SECTREGEX, line, re.IGNORECASE)
                currsection = thematch.group(1)
                # The name is proceeded by a number: "Input3"
                curritem = int(thematch.group(2)) if len(thematch.group(2)) > 0 else None

            elif currsection != 'Rules':
                [key, rawvalue] = line.split("=")

                if currsection == "System":
                    self.fisdict[currsection][key] = rawvalue.replace("'", "")

                elif currsection in ["Input", "Output"]:
                    if curritem not in self.fisdict[currsection]:
                        self.fisdict[currsection][curritem] = {
                            "MemberFunctions": {}
                        }

                    if key.startswith("MF"):
                        self.fisdict[currsection][curritem]["MemberFunctions"][int(key[2:])] = \
                            self._mflineparse(rawvalue)

                    elif key == "Range":
                        # Range is a space-separated array
                        self.fisdict[currsection][curritem]["Range"] = rawvalue[1:-1].split(" ")
                    else:
                        self.fisdict[currsection][curritem][key] = rawvalue[1:-1]


            elif currsection == 'Rules':
                """
                Example: 1 1, 3 (1) : 1

                Explanation here: 
                https://www.mathworks.com/help/fuzzy/building-systems-with-fuzzy-logic-toolbox-software.html

                Section 1: inputs: member function for each input to use
                Section 2: output: member function for each output to use
                Section 3 (in parens): weight
                Section 4 (after colon): shorthand for AND/OR  = 1/2  

                """
                # Rule expressed as a regex:
                ruleregex = "([-\d ]+),([-\d ]+)\((\d)\)\s*:\s*([\d]+)"
                rule = re.search(ruleregex, line)

                # Now match the MF number to a a label to make things easier later
                antecedents = self._ruleinoutparse(self.fisdict["Input"],
                                                   [int(idx) for idx in rule.group(1).strip().split(" ")])

                consequents = self._ruleinoutparse(self.fisdict["Output"],
                                                   [int(idx) for idx in rule.group(2).strip().split(" ")])

                self.fisdict[currsection].append({
                    "antecedents": antecedents,
                    "consequents": consequents,
                    "weight": int(rule.group(3).strip()),
                    "logic": "AND" if int(rule.group(4).strip()) == 1 else "OR",
                })


    @staticmethod
    def _ruleinoutparse(typelines, arr):
        """
        The rules section looks like this:

            [Rules]
            1 1 0 0, 3 (1) : 1
            1 -2 0 0, 2 (1) : 1

        The rule inputs and outputs aren't just integers:
            0 => means the input/output is not considered
            -3 => means (NOT)Input[MF3]

        This is maybe a little more explicit and verbose than we need to be but it's good for thoroughness and checking

        :param typelines: "Input", OR "Output" dictionary
        :param arr: Array of antecedent or consequent MF indeces
        :return: Tuple(InputName, MFlabel, notflag)
        """

        retval = []
        for inpnum, rawmfnum in enumerate(arr):
            inputname = typelines[inpnum + 1]["Name"]
            if (rawmfnum != 0):
                if rawmfnum < 0:
                    mfnum = int(math.fabs(rawmfnum))
                    notflag = True
                else:
                    mfnum = rawmfnum
                    notflag = False

                retval.append((inputname, typelines[inpnum + 1]["MemberFunctions"][mfnum]["label"], notflag))
        return retval


    @staticmethod
    def _mflineparse(mfstring):
        """
        Turn a member function line from the .fis file into something more understandable.

            MF1='Low':'trapmf',[0 0 0.1 0.25]
            MF2='Medium':'trapmf',[0.1 0.25 0.75 1]
            MF3='High':'trapmf',[0.75 1 100 100]


        :param mfstring:  Here's what's coming in: 'Low':'trapmf',[0 0 0.07 0.10]
        :return:
        """
        split1 = mfstring.split(":")
        split2 = split1[1].split(",")
        return {
            "label": split1[0].replace("'", ""),
            "func": split2[0].replace("'", ""),
            "points": [float(idx) for idx in split2[1][1:-1].split(" ")]
        }

    @staticmethod
    def _getshapefunc(shape):
        """
        Simply make an equivalence between a string from the fis file and the scikit fuzzy function
        :param shape:
        :return:
        """
        return {
            "dsigmf": fuzz.dsigmf,
            "gaussmf": fuzz.gaussmf,
            "gauss2mf": fuzz.gauss2mf,
            "gbellmf": fuzz.gbellmf,
            "piecemf": fuzz.piecemf,
            "pimf": fuzz.pimf,
            "psigmf": fuzz.psigmf,
            "sigmf": fuzz.sigmf,
            "smf": fuzz.smf,
            "trapmf": fuzz.trapmf,
            "trimf": fuzz.trimf,
            "zmf": fuzz.zmf
        }[shape]
