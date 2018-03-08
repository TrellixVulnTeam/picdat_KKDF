import logging
from os import sep

__author__ = 'Marie Lohbeck'
__copyright__ = 'Copyright 2018, Advanced UniByte GmbH'

# license notice:
#
# This file is part of PicDat.
# PicDat is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public (at your option) any later version.
#
# PicDat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with PicDat. If not,
# see <http://www.gnu.org/licenses/>.

# String to print together with the program name if user uses command line option --help or -h or
# any not recognized options:
HELP = '''
PicDat is a tool for visualizing performace data.
usage: %s [--help] [--sortbyname] [--inputfile "input"] [--outputdir "output"] [--debug "level"]
    --help, -h: prints this message
    --sortbyname, -s: Sorts the legends of most charts alphabetically. Per default, 
                      legend entries are sorted by relevance, means the graph with the
                      highest values in sum is displayed at the top of the legend.
    --inputfile "input", -i "input": input is the path to some perfstat output. Should be a 
                                     folder, .zip file, .data file, .out file, or .tgz file.
    --outputdir "output", -o "output": output is the directory's path, where this program puts its 
                                       results. If there is no directory existing yet under this 
                                       path, one would be created. If there already are some 
                                       PicDat results, they might be overwritten.
    --debug "level", -d "level": level should be inside debug, info, warning, error, critical. It 
                                 describes the filtering level of command line output during 
                                 running this program (default is "info").
    --logfile, -l: Redirects logging information into a file called picdat.log.
'''


# this log level is used, if the user didn't specify one:
DEFAULT_LOG_LEVEL = logging.INFO

# name of log file:
LOGFILE_NAME = 'picdat.log'

# program saves its results in a directory named like that (might have an additional number):
DEFAULT_DIRECTORY_NAME = 'results'

# program names csv files with the name of the chart they belong to, and the following ending:
CSV_FILE_ENDING = '_chart_values.csv'

# program names html file inside the result directory like this:
HTML_FILENAME = 'charts'
HTML_ENDING = '.html'

# this is the path to the text file the program uses as template to create the html head:
HTML_HEAD_TEMPLATE = 'templates' + sep + 'html_template.txt'

# these are the paths to the dygraph files the html document needs to show its charts:
DYGRAPHS_JS_SRC = 'templates' + sep + 'dygraph.js'
DYGRAPHS_CSS_SRC = 'templates' + sep + 'dygraph.css'

# these are the expected names of relevant files in xml mode:
XML_INFO_FILE = 'CM-STATS-HOURLY-INFO.XML'
XML_DATA_FILE = 'CM-STATS-HOURLY-DATA.XML'
XML_HEADER_FILE = 'HEADERS'
