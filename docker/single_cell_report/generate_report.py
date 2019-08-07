#!/usr/bin/python3

import subprocess as sp
import json
import argparse
import pandas as pd
import sys
import os
from jinja2 import Environment, FileSystemLoader

# some variables for common reference.
# many refer to keys set in the json file of
# config variables
TEMPLATE = 'template'
OUTPUT = 'output'
CFG = 'config_vars'
INPUT = 'input_file'
SCMATCH = 'scmatch_png'
GRAPH = 'graph_png'
KMEANS = 'kmeans_pngs'
SAMPLENAME = 'samplename'
CELLRANGER_VERSION = 'cellranger_version'
SCMATCH_VERSION = 'scmatch_version'
GIT_REPO = 'git_repo'
GIT_COMMIT = 'git_commit'
GENOME = 'genome'


class InputDisplay(object):
    '''
    A simple object to carry info to the markdown report.
    '''
    def __init__(self, sample_name, r1, r2):
        self.sample_name = sample_name
        self.r1 = r1
        self.r2 = r2


class AnnotationDisplay(object):
    '''
    A simple object to carry info to the markdown report.
    '''
    def __init__(self, sample_name, condition):
        self.name = sample_name
        self.condition = condition



def get_jinja_template(template_path):
    '''
    Returns a jinja template to be filled-in
    '''
    template_dir = os.path.dirname(template_path)
    env = Environment(loader=FileSystemLoader(template_dir), lstrip_blocks=True, trim_blocks=True)
    return env.get_template(
        os.path.basename(template_path)
    )


def run_cmd(cmd, return_stderr=False):
    '''
    Runs a command through the shell
    '''
    p = sp.Popen(cmd, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)
    stdout, stderr = p.communicate()
    if return_stderr:
        return stderr.decode('utf-8')
    return stdout.decode('utf-8')


def parse_input():
    '''
    Parses the commandline input, returns a dict
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', required=True, dest=TEMPLATE,
                        help="Template markdown report")
    parser.add_argument('--typing', required=True, dest=SCMATCH,
                        help="scMatch labeled tSNE cluster graph png")
    parser.add_argument('--graph', required=True, dest=GRAPH,
                        help="Graph clustering to cell typing png")
    parser.add_argument('--kmeans', required=True, dest=KMEANS, nargs='+',
                        help="Kmeans clustering graphs to cell typing png(s)")
    parser.add_argument('-o', required=True, dest=OUTPUT,
                        help="Name of output report file")
    parser.add_argument('-i', required=True, dest=INPUT,
                        help="Name of input FASTQ tarbell")
    parser.add_argument('-s', required=True, dest=SAMPLENAME,
                        help="sample name")
    parser.add_argument('--scmatch', required=True, dest=SCMATCH_VERSION,
                        help="scMatch version string")
    parser.add_argument('--cellranger', required=True, dest=CELLRANGER_VERSION,
                        help="cellranger version string")
    parser.add_argument('-j', required=True, dest=CFG,
                        help="Config file")
    args = parser.parse_args()
    return vars(args)


def fill_template(context, template_path, output):
    if os.path.isfile(template_path):
        template = get_jinja_template(template_path)
        with open(output, 'w') as fout:
            fout.write(template.render(context))
    else:
        print('The report template was not valid: %s' % template_path)
        sys.exit(1)


if __name__ == '__main__':

    # parse commandline args and separate the in/output from the
    # context variables
    arg_dict = parse_input()
    output_file = arg_dict.pop(OUTPUT)
    input_template_path = arg_dict.pop(TEMPLATE)


    # parse the json file which has additional variables
    j = json.load(open(arg_dict[CFG]))

    # alter how the files are displayed:
    r1_files = arg_dict[R1]
    r1_files = [r.split('/')[-1] for r in r1_files]
    r2_files = arg_dict[R2]
    r2_files = [r.split('/')[-1] for r in r2_files]
    samples = [os.path.basename(x)[:-len('_R1.fastq.gz')] for x in r1_files]
    file_display = []
    for r1, r2, s in zip(r1_files, r2_files, samples):
        ipd = InputDisplay(s, r1, r2)
        file_display.append(ipd)


    # make the context dictionary
    context = {}
    context.update(versions_dict)
    context.update(arg_dict)
    context.update(j)
    
    context.update({'file_display': file_display})

    # fill and write the completed report:
    fill_template(context, input_template_path, output_file)
