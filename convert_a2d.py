"""
Provide analog waveform input, get digitial transitions as output.
"""

import csv

# TODO: Add an argument parser
#     TODO: Add defaults to the values that are not required
# TODO: Possibly move calculated values into an object
# TODO: Break up code into functions
# TODO: Refactor
# TODO: Test

def main():

    # Collect input from user
    input_file = args[1]
    output_file = args[2]
    delimiter = args[3]
    num_of_header_lines = args[4]
    high_threshold_ratio = args[5]
    low_threshold_ratio = args[6]

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

        for input_row in csv_input:
            if (input_row[1] > high_thresh and digital_value == False) or
               (input_row[1] < low_thresh and digital_value == True):

                digital_value = not digital_value
                csv_output.writerow([row1[0], int(digital_value)])
                threshold_count += 1

    print("Found {0} transitions in input file".format(threshold_count))


if __name__ == "__main__":
    main()
