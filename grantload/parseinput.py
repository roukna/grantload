import sys
import os
import csv


def parse_input(input_file, output_file):
    cwd = os.getcwd()
    script_file = cwd + "/parse_script.sh"
    os.system("chmod 774 {}".format(script_file))
    os.system("sh parse_script.sh %s" %(input_file))
    out_row = []

    with open(input_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        for i, row in enumerate(reader):
            out_col = []
            for column_val in row:
                column_val = column_val.replace('"','')
                out_col.append(column_val)
            print out_col
            out_row.append(out_col)

    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(out_row)

    os.remove(input_file)


def main(argv1, argv2):
    parse_input(argv1, argv2)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
