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

    # TODO: Monster comment describing special case
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

def write_crossings_file(input_data_stream, thresholds, delimiter, num_of_header_lines, output_file):
    """
    Writes analog data in input file as digital transitions into output file.
    @input_file - In: Path to input csv file containing analog data
    @thresholds - In: Thresholds namedtuple containing thresholds (low, high, middle)
    @num_of_header_lines - In: Number of header lines before analog data
    @output_file - In: Path to output csv file to store digital transitions
    @return - Out: Number of transitions found in input file
    """

    # Going through file getting transitions
    with open(output_file, mode='w', newline='') as output_data:
        csv_output = csv.writer(output_data, delimiter=delimiter) # Get csv writer

        # Initialize values
        first_row = next(input_data_stream)
        analog_value = first_row[1]
        digital_value = analog_value > thresholds.middle
        threshold_count = 0

        # Write initial row
        csv_output.writerow([first_row[0], int(digital_value)])

        # Write the rest of the rows in transitions
        for input_row in input_data_stream:
            current_value = input_row[1]
            if (current_value > thresholds.high_thresh and not digital_value) or \
               (current_value < thresholds.low_thresh and digital_value):

                digital_value = not digital_value
                csv_output.writerow([input_row[0], int(digital_value)])
                threshold_count += 1

    return threshold_count

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

    threshold_count = write_crossings_file(input_stream, \
                               thresholds, input_arguments.delimiter, \
                               input_arguments.headers, input_arguments.output)

    print("Found {0} transitions in input file".format(threshold_count))


if __name__ == "__main__":
    main()
