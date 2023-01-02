import math

def print_bar(percent):
    # round to the nearest integer
    perc = math.ceil(percent)
    negative = 100 - perc
    # Depending on the percentage, and adequate number of '#' and '-' are printed
    bar = '[' + perc * '#' + negative * '-' + ']' + ' {}%'.format(perc)
    
    # since 'percent' could end up being something like 99.999999993
    # we simply account for this case by rounding and checking
    if round(percent, 3) == 99.999 or round(percent, 3) == 100.000:
        print(" " * 110)
    else:
        # print with carriage return if it isn't yet at 100%
        print(bar, end='\r')
