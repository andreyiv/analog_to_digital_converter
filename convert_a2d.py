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

def write_output_file(transitions, delimiter, output_file_path):
    with open(output_file_path, mode='w', newline='') as output_file:
        csv_output = csv.writer(output_file, delimiter=delimiter)

        for tr in transitions:
            csv_output.writerow([tr[0]] + list(map(int, tr[1:])))

def get_digital_value(previous_digital_value, current_analog_value, thresholds):
    if current_analog_value > thresholds.high_thresh:
        return True
    elif current_analog_value < thresholds.low_thresh:
        return False
    else:
        return previous_digital_value


def threshold_crossings(input_data_streams, thresholds_list):
    # Because a transition is going above a threshold value when
    # current value is 0 or below threshold when current value is 1 and
    # we don't have the current value we need to make an assumption of one.
    # For better or worse, the assumption is:
    # below middle of analog range = 0, above middle = 1
    analog_values = [next(s) for s in input_data_streams]
    sample_meta = analog_values[0][0] # XXX: I'll regret this later
    analog_values = [av[1] for av in analog_values]
    digital_values = [av > th.middle for (av, th) in zip(analog_values, thresholds_list)]

    yield [sample_meta] + digital_values

    while (len(analog_values)): # TODO: Change this to something that actually works
        cur_digital_values = [get_digital_value(pdv, cav, th) for (pdv, cav, th) in zip(digital_values, analog_values, thresholds_list)]
        digital_transitions = [pdv ^ cdv for (pdv, cdv) in zip(digital_values, cur_digital_values)]
        if any(digital_transitions):
            yield [sample_meta] + cur_digital_values
            digital_values = cur_digital_values
        analog_values = [next(s) for s in input_data_streams]
        sample_meta = analog_values[0][0]
        analog_values = [av[1] for av in analog_values]


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

    input_streams = [get_input_stream(fname, \
                                    input_arguments.headers, \
                                    input_arguments.delimiter) for fname in input_arguments.input]

    limits_list = [find_min_max(stream) for stream in input_streams]

    thresholds_list = [calculate_thresholds(lim.min, lim.max, \
                                      input_arguments.lratio, \
                                      input_arguments.hratio) for lim in limits_list]

    input_streams = [get_input_stream(fname, \
                                    input_arguments.headers, \
                                    input_arguments.delimiter) for fname in input_arguments.input]

    transitions = threshold_crossings(input_streams, thresholds_list)

    write_output_file(transitions, input_arguments.delimiter, \
                                   input_arguments.output)

    # print("Found {0} transitions in input file".format(threshold_count))


if __name__ == "__main__":
    main()
