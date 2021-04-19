import math
def printbar(percent):
    # Depending on the percentage, and adequate number of '#' and '-' are printed
    perc = math.ceil(percent)
    negative = 100-perc
    bar = '[' + perc*'#' + negative*'-'+ ']' + ' %f%% done.' % percent
    # use \r at the end to prevent it to print multiple lines
    print(bar, end='\r')