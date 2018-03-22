import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import re
class FisModel:
    SECTIONS = [

    ]
    SECTREGEX = "^\[(.*)\]"
    def __init__(self, filename):
        lines = [line for line in open('filename')]
        linedict = {}

        currSection = ""

        # Loop over all non-blank lines
        for line in [l for l in lines if l.strip != ""]:
            if (re.match(line, self.SECTREGEX))
                thematch = re.search(line, self.SECTREGEX, re.IGNORECASE)
                currSection = thematch.group(1)



class System:
    def __init__(self, lines):
        for line in lines:
            print "hi"

class Input:
    def __init__(self, lines):
        for line in lines:
            print "hi"

class Output(Input):

    def __init__(self, lines):
        for line in lines:
            print "hi"

class Rules:
    def __init__(self, lines):
        for line in lines:
            print "hi"