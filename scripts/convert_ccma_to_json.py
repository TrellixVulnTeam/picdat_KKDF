import logging
import os
import sys
import shutil
import getopt
import tarfile
import uuid
import yaml
import requests

__author__ = 'Marie Lohbeck'
__copyright__ = 'Copyright 2018, Advanced UniByte GmbH'


def get_log_level(log_level_string):
    """
    Turns a string into a log level, the logging module can understand
    :param log_level_string: A String representing a log level like 'info' or 'error'.
    :return: A constant from the logging module, representing a log level.
    """
    log_level_dict = {
        'debug': logging.DEBUG,
        'DEBUG': logging.DEBUG,
        'info': logging.INFO,
        'INFO': logging.INFO,
        'warning': logging.WARNING,
        'WARNING': logging.WARNING,
        'error': logging.ERROR,
        'ERROR': logging.ERROR,
        'critical': logging.CRITICAL,
        'CRITICAL': logging.CRITICAL
    }
    try:
        return log_level_dict[log_level_string]
    except KeyError:
        logging.error('No log level like \'%s\' exists. Try one of those: %s', log_level_string,
                      [entry for entry in log_level_dict])
        sys.exit(1)


def handle_user_input(argv):
    # get all options from argv and turn them into a dict
    try:
        opts, _ = getopt.getopt(argv[1:], 'hld:i:o:',
            ['help', 'logfile', 'debug=', 'input=', 'outputdir='])
        opts = dict(opts)
    except getopt.GetoptError:
        logging.error('Couldn\'t read command line options.')

    # print help information if option 'help' is given
    if '-h' in opts or '--help' in opts:
        print('''
usage: %s [--help] [--input "input"] [--outputdir "output"] [--debug "level"]

    --help, -h: prints this message
                      
    --input "input", -i "input": input is the path to an ASUP tgz
                                 
    --outputdir "output", -o "output": output is the directory's path, where this program puts its
                                       results. If there is no directory existing yet under this
                                       path, one would be created.
                                       
    --debug "level", -d "level": level should be inside debug, info, warning, error, critical. It
                                 describes the filtering level of command line output during
                                 running this program. Default is "info".
                                 
    --logfile, -l: redirects logging information into a file called conversion.log.
        ''' % argv[0])

    # extract log level from options if possible
    if '-d' in opts:
        log_level = get_log_level(opts['-d'])
    elif '--debug' in opts:
        log_level = get_log_level(opts['--debug'])
    else:
        log_level = logging.INFO

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=log_level)

    # extract inputfile from options if possible
    if '-i' in opts:
        input_file = opts['-i']
    elif '--input' in opts:
        input_file = opts['--input']
    else:
        while True:
            input_file = input('Please enter a path to a ASUP tgz:' + os.linesep)

            if os.path.isfile(input_file):
                break
            else:
                print('This file does not exist. Try again.')
    if not os.path.isfile(input_file):
        print('input file does not exist.')
        sys.exit(1)

    # extract outputdir from options if possible
    if '-o' in opts:
        output_dir = opts['-o']
    elif '--outputdir' in opts:
        output_dir = opts['--outputdir']
    else:
        output_dir = input('Please select a destination directory for the json files. ('
                                      'Default is ./picdat_json_files):' + os.linesep)
        if output_dir == '':
            output_dir = 'picdat_json_files'

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # decide, whether logging information should be written into a log file
    if '-l' in opts or '--logfile' in opts:
        _ = [logging.root.removeHandler(handler) for handler in logging.root.handlers[:]]
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename=output_dir
                            +os.sep + 'conversion.log', level=log_level)

    logging.info('inputfile: %s, outputdir: %s', os.path.abspath(input_file), os.path.abspath(
        output_dir))

    return os.path.abspath(input_file), os.path.abspath(output_dir)


def read_config():
    try:
        with open('config.yml', 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        trafero_in_dir = cfg['trafero_in_dir']
        trafero_address = cfg['trafero_address']
        objects = cfg['objects']

        return trafero_in_dir, trafero_address, objects
    except FileNotFoundError:
        logging.error('No config file. Script needs a file named config.yml in the same location.')
        sys.exit(1)
    except KeyError:
        logging.error('Invalid config file. config.yml needs to include entries '
                      '"trafero_in_dir", "trafero_address" and "objects".')
        sys.exit(1)


def copy_tgz_to_trafero(abs_asup_path, input_file):
    os.makedirs(abs_asup_path)
    with tarfile.open(input_file, 'r') as tar:
        tar.extractall(abs_asup_path)


def get_list_string(l):
    list_string = '['
    for element in l:
        list_string += '"' + str(element) + '"'
        list_string += ','
    list_string = list_string[:-1]
    list_string += ']'
    return list_string


def ingest_into_trafero(header, objects_counters_dict, asup_path, trafero_address):
    objects_str = get_list_string((list(objects_counters_dict.keys())))
    data = '{"ccma_dir_path":"","ingest_type":"asup","asup_dir_path":"%s","object_filter":%s,' \
    '"display_all_zeros":false}' % (asup_path, objects_str)
    logging.debug('payload ingest request: %s', data)

    url = '%s/api/manage/ingest/' % trafero_address
    logging.debug('url ingest request: %s', url)

    response = requests.post(url, headers=header, data=data)
    logging.debug('ingest response: %s', response.text)

    cluster_uuid = response.json()['ingest_results'][0]['cluster_uuid']
    node_uuid = response.json()['ingest_results'][0]['node_uuid']
    logging.debug('cluster uuid: %s, node uuid: %s', cluster_uuid, node_uuid)

    return cluster_uuid, node_uuid


def retrieve_values(header, objects_counters_dict, cluster, node, trafero_address, output_dir):
    url = '%s/api/retrieve/values/' % trafero_address
    logging.debug('url retrieve values request: %s', url)

    for obj, counters in objects_counters_dict.items():

        logging.debug('counters (%s): %s', obj, counters)
        counter_string = get_list_string(counters)

        data = '{"cluster":"%s","node":"%s","object_name":"%s","counter_name":"",'\
        '"counter_names":%s,"instance_name":"","x_label":"","y_label":"","time_from":0,'\
        '"time_to":0,"summary_type":"","best_effort":false,"raw":false}' \
        % (cluster, node, obj, counter_string)
        logging.debug('payload retrieve values request (%s): %s', obj, data)

        value_file = os.path.join(output_dir, str(obj) + '.json')
        with requests.get(url, headers=header, data=data, stream=True) as response:
            with open(value_file, 'wb') as values:
                for chunk in response.iter_content(chunk_size=1024):
                    logging.debug('chunk: %s', chunk)
                    values.write(chunk)


def delete_from_trafero(header, cluster, node, trafero_address, abs_asup_path):
    url = '%s/api/manage/delete/' % trafero_address
    data = '{"cluster":"%s","node":"%s"}' % (cluster, node)

    requests.delete(url, headers=header, data=data)

    shutil.rmtree(abs_asup_path)


INPUT_FILE, OUTPUT_DIR = handle_user_input(sys.argv)
TRAFERO_COLLECTOR, TRAFERO_ADDRESS, OBJECTS_COUNTERS_DICT = read_config()
ASUP_PATH = str(uuid.uuid4())
ABS_ASUP_PATH = os.path.join(TRAFERO_COLLECTOR, ASUP_PATH)
copy_tgz_to_trafero(ABS_ASUP_PATH, INPUT_FILE)

REQUEST_HEADER = {'Content-Type': 'application/json', 'Accept': 'application/json'}

CLUSTER, NODE = ingest_into_trafero(
    REQUEST_HEADER, OBJECTS_COUNTERS_DICT, ASUP_PATH, TRAFERO_ADDRESS)
retrieve_values(REQUEST_HEADER, OBJECTS_COUNTERS_DICT, CLUSTER, NODE, TRAFERO_ADDRESS, OUTPUT_DIR)
delete_from_trafero(REQUEST_HEADER, CLUSTER, NODE, TRAFERO_ADDRESS, ABS_ASUP_PATH)
