"""
Provide analog waveform input, get digitial transitions as output.
"""

import argparse
import csv

# TODO: Provide limits on ratios
# TODO: Possibly move calculated values into an object
# TODO: Break up code into functions
# TODO: Refactor
# TODO: Test

# Create argument parser
parser = argparse.ArgumentParser()
parser.add_argument("input", help="path to input csv file of analog data")
parser.add_argument("output", help="path to output csv file of digital transitions")
parser.add_argument("-d", "--delimiter", help="specify delimiter used in input and output, ',' is used by default")
parser.add_argument("-n", "--headers", type=int, help="number of header rows in input")
parser.add_argument("-r", "--lratio", type=float, help="ratio of 1 to 0 crossing")
parser.add_argument("-R", "--hratio", type=float, help="ratio of 0 to 1 crossing")

def main():

    # Parse arguments
    input_arguments = parser.parse_args()

    # Collect input from user
    input_file = input_arguments.input
    output_file = input_arguments.output
    delimiter = input_argumets.delimiter if input_arguments.delimiter else ','
    num_of_header_lines = input_arguments.headers if input_arguments.headers else 1
    low_threshold_ratio = input_arguments.lratio if input_arguments.lratio else 1/3
    high_threshold_ratio = input_arguments.hratio if input_arguments.hratio else 2/3

    maximum = 0
    minimum = 0

    # Opening file once to read through
    # with open(input_file, 'rb') as input_data:
    with open(input_file, newline='') as input_data:
        csv_input = csv.reader(input_data, delimiter=delimiter) # Get csv reader

        # Ignoring header information
        for i in range(num_of_header_lines):
            next(csv_input)  # Throwing away header data

        # Initializing max and min
        maximum = next(csv_input)[1]
        minimum = maximum

        # Finiding max and min
        for row in csv_input:

            if maximum < row[1]:
                maximum = row[1]

            if minimum > row[1]
                minimum = row[1]


    # Calculate thresholds and middle analog value
    analog_range = maximum - minimum
    middle = analog_range / 2
    high_thresh = analog_range * high_threshold_ratio
    low_thresh = analog_range * low_threshold_ratio


    # Opening file one more time to read through
    # with open(input_file, 'rb') as input_data
         # open(output_file, 'rb') as output_data:
    with open(input_file, newline='') as input_data
         open(output_file, newline='') as output_data:
        csv_input = csv.reader(input_data, delimiter=delimiter) # Get csv reader
        csv_output = csv.writer(output_data, delimiter=delimiter) # Get csv writer

        # Funnel headers over to the output
        for i in range(num_of_header_lines):
            csv_output.writerow(csv_input.next())

        # Initialize values
        row1 = csv_input.next()
        analog_value = row1[1]
        digital_value = False if analog_value < middle else True
        threshold_count = 0

        # Write initial row
        csv_output.writerow([row1[0], int(digital_value)])

        # Write the rest of the rows in transitions
        for input_row in csv_input:
            if (input_row[1] > high_thresh and digital_value == False) or
               (input_row[1] < low_thresh and digital_value == True):

                digital_value = not digital_value
                csv_output.writerow([row1[0], int(digital_value)])
                threshold_count += 1

    print("Found {0} transitions in input file".format(threshold_count))


if __name__ == "__main__":
    main()

