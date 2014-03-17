"""
Converts n analog waveforms to digital transitions.
"""

import argparse
import csv
from collections import namedtuple

# TODO: Provide error output for header argument too small, and invalid input ratios
# TODO: Provide output if input streams are of different length 
# TODO: Write unit tests
# TODO: Add progress reporting

Limits = namedtuple('Limits', ['min', 'max'])
Thresholds = namedtuple('Thresholds', ['low_thresh', 'high_thresh', 'middle'])

def get_input_stream(input_file_path, num_header_lines, delimiter):
    """
    Parses a csv file line by line creating a generator with a list with data.
    """
    with open(input_file_path, mode='r', newline='') as input_data:
        csv_input = csv.reader(input_data, delimiter=delimiter)

        # Ignoring header information
        for i in range(num_header_lines):
            next(csv_input)

        for row in csv_input:
            yield (row[0], float(row[1]))

def find_min_max(input_data_stream):
    """
    Returns a named tuple of Limits (min, max) by consuming
    a stream type object.
    """
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
    Returns a namedtuple of threshold data (low_thresh, high_thresh, middle)
    based on a set of inputs.
    """
    analog_range = maximum - minimum
    return Thresholds(low_thresh = analog_range * low_thresh_ratio, \
                      high_thresh = analog_range * high_thresh_ratio, \
                      middle = analog_range / 2)

def write_output_file(transitions, delimiter, num_streams, output_file_path):
    """
    Writes out a stream type object of lists into a csv file.
    """
    with open(output_file_path, mode='w', newline='') as output_file:
        csv_output = csv.writer(output_file, delimiter=delimiter)

        # Write header
        csv_output.writerow(['sample'] + list(range(num_streams)))
        # Continue with the rest of the data
        for tr in transitions:
            csv_output.writerow([tr[0]] + list(map(int, tr[1:])))

def get_digital_value(previous_digital_value, current_analog_value, thresholds):
    """
    Outputs current digital value. No mans land between two thresholds means
    no transition so current value = previous value.
    """
    if current_analog_value > thresholds.high_thresh:
        return True
    elif current_analog_value < thresholds.low_thresh:
        return False
    else:
        return previous_digital_value


def threshold_crossings(input_data_streams, thresholds_list):
    """
    Generates threshold crossings/transitions from an analog data stream
    and a set of threshold values. Works on one or more streams/threshold sets
    but all need to be the same length.
    """
    # Initialize values
    analog_values = [next(s) for s in input_data_streams]
    sample_meta = analog_values[0][0] # Sample count or time data
    # Strip out sample_meta out of analog_values as it's not used
    analog_values = [av[1] for av in analog_values]

    # Because a transition is going above a threshold value when
    # current value is 0 or below threshold when current value is 1 and
    # we don't have the current value we need to make an assumption of one.
    # For better or worse, the assumption is:
    # below middle of analog range = 0, above middle = 1
    digital_values = [av > th.middle for (av, th) in \
                      zip(analog_values, thresholds_list)]

    # Provide initial value (special case)
    yield [sample_meta] + digital_values

    # TODO: Try to roll this /\ initialization step into the main loop \/

    while len(analog_values):
        cur_digital_values = [get_digital_value(pdv, cav, th) for (pdv, cav, th) in \
                              zip(digital_values, analog_values, thresholds_list)]
        digital_transitions = [pdv ^ cdv for (pdv, cdv) in \
                               zip(digital_values, cur_digital_values)]
        if any(digital_transitions):
            yield [sample_meta] + cur_digital_values
            digital_values = cur_digital_values
        # Advance the iterators for next step
        analog_values = [next(s) for s in input_data_streams]
        sample_meta = analog_values[0][0]
        analog_values = [av[1] for av in analog_values]


def get_argumets():
    """
    Parse the input arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs='+', help="path to input csv files of \
                                        analog data, minimum of one")
    parser.add_argument("output", help="path to output csv file of digital transitions")
    parser.add_argument("-d", "--delimiter", default=',', \
                                        help="specify delimiter used in \
                                        input and output, ',' by default")
    parser.add_argument("-n", "--headers", type=int, default=1, \
                                        help="number of header rows in input")
    parser.add_argument("-r", "--lratio", type=float, default=1/3, \
                                        help="ratio of 1 to 0 crossing")
    parser.add_argument("-R", "--hratio", type=float, default=2/3, \
                                        help="ratio of 0 to 1 crossing")
    return parser.parse_args()

def main():

    # Parse arguments
    args = get_argumets()

    print('Reading input files: {0}.'.format(', '.join(args.input)))
    # Get list of streams of input data to figure out thresholds
    input_streams = [get_input_stream(fname, args.headers, \
                                    args.delimiter) for fname in args.input]

    # Get list of Limits
    limits_list = [find_min_max(stream) for stream in input_streams]

    # Get list of thresholds from inputs by using individual limits
    thresholds_list = [calculate_thresholds(lim.min, lim.max, \
                                            args.lratio, args.hratio) \
                                            for lim in limits_list]

    # Read input one more time to generate transitions from the data
    input_streams = [get_input_stream(fname, args.headers, args.delimiter) \
                                            for fname in args.input]

    # Get digital threshold crossings/transitions
    transitions = threshold_crossings(input_streams, thresholds_list)

    # Write out one csv file containing all streams
    write_output_file(transitions, args.delimiter, len(args.input), args.output)
    print('Wrote transition data to {0}.'.format(args.output))


if __name__ == "__main__":
    main()
