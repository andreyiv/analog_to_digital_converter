"""
Provide analog waveform input, get digitial transitions as output.
"""

import argparse
import csv
import pdb

# TODO: Provide limits on ratios
# TODO: Possibly move calculated values into an object
# TODO: Break up code into functions
# TODO: Refactor
# TODO: Test

# Create argument parser
parser = argparse.ArgumentParser()
parser.add_argument("input", help="path to input csv file of analog data")
parser.add_argument("output", help="path to output csv file of digital transitions")
parser.add_argument("-d", "--delimiter", default=',', help="specify delimiter used in input and output, ',' is used by default")
parser.add_argument("-n", "--headers", type=int, default=1, help="number of header rows in input")
parser.add_argument("-r", "--lratio", type=float, default=1/3, help="ratio of 1 to 0 crossing")
parser.add_argument("-R", "--hratio", type=float, default=2/3, help="ratio of 0 to 1 crossing")

def main():

    # Parse arguments
    input_arguments = parser.parse_args()

    # Collect input from user
    input_file = input_arguments.input
    output_file = input_arguments.output
    delimiter = input_argumets.delimiter
    num_of_header_lines = input_arguments.headers
    low_threshold_ratio = input_arguments.lratio
    high_threshold_ratio = input_arguments.hratio

    maximum = 0
    minimum = 0

    # Opening file once to read through
    with open(input_file, mode='r', newline='') as input_data:
        csv_input = csv.reader(input_data, delimiter=delimiter) # Get csv reader

        # Ignoring header information
        for i in range(num_of_header_lines):
            next(csv_input)  # Throwing away header data

        # Initializing max and min
        maximum = float(next(csv_input)[1]) # TODO: provide a good error code for when it's not a float
        minimum = maximum

        # Finiding max and min
        for row in csv_input:

            current_value = float(row[1])
            if maximum < current_value:
                maximum = current_value

            if minimum > current_value:
                minimum = current_value


    # Calculate thresholds and middle analog value
    analog_range = maximum - minimum
    middle = analog_range / 2
    high_thresh = analog_range * high_threshold_ratio
    low_thresh = analog_range * low_threshold_ratio


    # Opening file one more time to read through
    with open(input_file, mode='r', newline='') as input_data, \
         open(output_file, mode='w', newline='') as output_data:
        csv_input = csv.reader(input_data, delimiter=delimiter) # Get csv reader
        csv_output = csv.writer(output_data, delimiter=delimiter) # Get csv writer

        # Funnel headers over to the output
        for i in range(num_of_header_lines):
            csv_output.writerow(next(csv_input))

        # Initialize values
        row1 = next(csv_input)
        analog_value = float(row1[1])
        digital_value = False if analog_value < middle else True
        threshold_count = 0

        # Write initial row
        csv_output.writerow([row1[0], int(digital_value)])

        # Write the rest of the rows in transitions
        for input_row in csv_input:
            current_value = float(input_row[1])
            if (current_value > high_thresh and digital_value == False) or \
               (current_value < low_thresh and digital_value == True):

                digital_value = not digital_value
                csv_output.writerow([input_row[0], int(digital_value)])
                threshold_count += 1

    print("Found {0} transitions in input file".format(threshold_count))


if __name__ == "__main__":
    main()

