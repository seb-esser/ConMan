import math


def print_bar(percent):
    # Depending on the percentage, and adequate number of '#' and '-' are printed
    perc = math.ceil(percent)
    negative = 100 - perc
    bar = '[' + perc * '#' + negative * '-' + ']' + ' %d%% done.' % perc
    # use \r at the end to prevent it to print multiple lines
    if percent != 100:
        print(bar, end='\r')
    else:
        print(bar)
