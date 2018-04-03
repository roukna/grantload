import sys
import os
import csv

def main(argv1):
    input_file = argv1
    # print input_file
    script_file = "parse_script.sh"
    os.system("chmod 774 {}".format(script_file))
    os.system("sh parse_script.sh %s" %(input_file))
    with open(input_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for row in reader:
            for column_val in row:
                print column_val
                column_val = column_val.replace('\"','')
                print column_val
                

if __name__ == '__main__':
    main(sys.argv[1])
