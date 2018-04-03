import sys
import os
import csv

def parse_input(input_file):
    # print input_file
    script_file = "parse_script.sh"
    os.system("chmod 774 {}".format(script_file))
    os.system("sh parse_script.sh %s" %(input_file))
    with open(input_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            for column_val in row:
                column_val = column_val.replace('\"','')
