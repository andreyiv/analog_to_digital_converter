"""
Provide analog waveform input, get digitial transitions as output.
"""

import argparse
import csv
from collections import namedtuple

# TODO: Provide limits on ratios
# TODO: Refactor
# TODO: Test

Limits = namedtuple('Limits', ['min', 'max'])
Thresholds = namedtuple('Thresholds', ['low_thresh', 'high_thresh', 'middle'])

def get_input_stream(input_file_path, num_header_lines, delimiter):

    # Opening file stream to get data
    with open(input_file_path, mode='r', newline='') as input_data:
        csv_input = csv.reader(input_data, delimiter=delimiter) # Get csv reader

        # Ignoring header information
        for i in range(num_header_lines):
            next(csv_input)  # Throwing away header data

        for row in csv_input:
            yield (row[0], float(row[1])) # TODO: provide a good error code for when it's not a float

def find_min_max(input_data_stream):

    minimum = next(input_data_stream)[1]
    maximum = minimum

    # Finiding max and min
    for row in input_data_stream:

        current_value = float(row[1])
        if minimum > current_value:
            minimum = current_value

        if maximum < current_value:
            maximum = current_value

    return Limits(min = minimum, max = maximum)

def calculate_thresholds(minimum, maximum, low_thresh_ratio, high_thresh_ratio):
    """
    Calculates thresholds and returns as Threshold namedtuple
    @minimum - In: Minimum value
    @maximum - In: Maximum value
    @low_thresh_ratio - In: Ratio generating low_thresh
    @high_thresh_ratio - In: Ratio generating high_thresh
    @return - Out: Threshold namedtuple with low and high_thresh, and middle
    """
    analog_range = maximum - minimum
    return Thresholds(low_thresh = analog_range * low_thresh_ratio, \
                      high_thresh = analog_range * high_thresh_ratio, \
                      middle = analog_range / 2)

def write_output_file(input_data_stream, delimiter, thresholds, output_file_path):
    with open(output_file_path, mode='w', newline='') as output_file:
        csv_output = csv.writer(output_file, delimiter=delimiter)

        for crossing in threshold_crossings(input_data_stream, thresholds):
            csv_output.writerow(crossing)

def threshold_crossings(input_data_stream, thresholds):

    # TODO: Monster comment describing special case
    first_row = next(input_data_stream)
    analog_value = first_row[1]
    digital_value = analog_value > thresholds.middle

    # Write initial row
    yield [first_row[0], int(digital_value)]

    # Write the rest of the rows in transitions
    for input_row in input_data_stream:
        current_value = input_row[1]
        if (current_value > thresholds.high_thresh and not digital_value) or \
           (current_value < thresholds.low_thresh and digital_value):

            digital_value = not digital_value
            yield [input_row[0], int(digital_value)]

def get_argumets():

    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs='+', help="path to input csv files of analog data, minimum of one")
    parser.add_argument("output", help="path to output csv file of digital transitions")
    parser.add_argument("-d", "--delimiter", default=',', help="specify delimiter used in input and output, ',' is used by default")
    parser.add_argument("-n", "--headers", type=int, default=1, help="number of header rows in input")
    parser.add_argument("-r", "--lratio", type=float, default=1/3, help="ratio of 1 to 0 crossing")
    parser.add_argument("-R", "--hratio", type=float, default=2/3, help="ratio of 0 to 1 crossing")

    return parser.parse_args()

def main():

    # Parse arguments
    input_arguments = get_argumets()

    input_stream = get_input_stream(input_arguments.input[0], \
                                    input_arguments.headers, \
                                    input_arguments.delimiter)

    lim = find_min_max(input_stream)

    thresholds = calculate_thresholds(lim.min, lim.max, \
                    input_arguments.lratio, input_arguments.hratio)

    input_stream = get_input_stream(input_arguments.input[0], \
                                    input_arguments.headers, \
                                    input_arguments.delimiter)

    write_output_file(input_stream, input_arguments.delimiter, \
                             thresholds, input_arguments.output)

    # print("Found {0} transitions in input file".format(threshold_count))


if __name__ == "__main__":
    main()
