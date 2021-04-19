import math
def printbar(percent):
    perc = math.ceil(percent)
    negative = 100-perc
    bar = '[' + perc*'#' + negative*'-'+ ']' + ' %f%% done.' % percent
    print(bar, end='\r')