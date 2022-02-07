import xml.etree.ElementTree as ElementTree
import calendar
import time
import sys
import os
import re
import argparse


def create_raw_output_file(file_name, rawfile="raw_output.csv"):
    """This function opens the xml file and parses the output. It then creates a CSV file with all keywords and timing details.
    This CSV will later be parsed and summarized and then the raw data file will be removed."""

    tree = ElementTree.parse(file_name)
    with open(rawfile, "a") as f:
        for kw in tree.findall(".//kw"):
            status = kw.find('./status')
            keyword = kw.attrib['name']
            try:
                keyword = kw.attrib['type'] + " " + keyword
            except:
                keyword = keyword
            keyword = clean_keyword(keyword)
            kwstatus = status.attrib['status']
            starttime = status.attrib['starttime']
            endtime = status.attrib['endtime']

            start_epoch = calendar.timegm(time.strptime(starttime, '%Y%m%d %H:%M:%S.%f'))
            end_epoch = calendar.timegm(time.strptime(endtime, '%Y%m%d %H:%M:%S.%f'))
            duration = end_epoch - start_epoch

            f.write(f"{keyword};{kwstatus};{duration};{starttime};{endtime}\n")


def clean_keyword(keyword):
    # remove all pre words from BDD syntax
    if keyword.lower().startswith('given'):
        keyword = keyword[6:]
    elif keyword.lower().startswith('when'):
        keyword = keyword[5:]
    elif keyword.lower().startswith('then'):
        keyword = keyword[5:]
    elif keyword.lower().startswith('and'):
        keyword = keyword[4:]

    # remove variable names
    keyword = re.sub("'.+'", "''", keyword)

    return keyword


def parse_raw_output_file(output="output.csv", rawfile="raw_output.csv"):
    """ This function takes the CSV that already has the parsed data. It contains the keywords and the timing details.
        This function creates an output file with all aggregated data"""

    with open(rawfile, 'r') as f:
        lines = f.readlines()

    keywords = []
    unique_keywords = []

    for line in lines:
        elements = line.split(";")
        keywords.append(elements[0])

    unique_keywords = set(keywords)

    with open(output, "a") as f:
        # create csv header first
        f.write(f"keyword;occurences;total_time;average;longest \n")

        for keyword in unique_keywords:
            occurences = 0
            total_time = 0
            longest = 0
            average = 0

            for k in lines:
                elements = k.split(";")
                if elements[0] == keyword:
                    occurences += 1
                    total_time += int(elements[2])
                    if int(elements[2]) > longest:
                        longest = int(elements[2])
            average = total_time / occurences
            f.write(f"{keyword};{occurences};{total_time};{average};{longest}\n")

    os.remove(rawfile)


def create_raw_output_files(input_files):
    files = input_files.split(",")
    for file in files:
        create_raw_output_file(file)


def main(input_files, output_file):
    create_raw_output_files(input_files)
    parse_raw_output_file(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Welcome to the Robot framework output parser",
        epilog="This script will pass a robot output xml and generates a CSV containing "
               "the number of times a function is called and the average time it took to complete the keyword.")
    parser.add_argument("-i", "--input_file", type=str, default="output.xml",
                        help="The path to the output.xml file", required=True)
    parser.add_argument("-o", "--output_file", type=str, default="output.csv",
                        help="The output file name (should end with .csv)", required=True)
    args = parser.parse_args()

    sys.exit(main(args.input_file, args.output_file))
