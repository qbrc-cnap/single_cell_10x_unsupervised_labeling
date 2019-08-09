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
SCMATCH_HASH = 'scmatch_git_commit_hash'
SCMATCH_URL = 'scmatch_git_repo_url'
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
    parser.add_argument('--scmatchhash', required=True, dest=SCMATCH_HASH,
                        help="scMatch git commit hash")
    parser.add_argument('--scmatchurl', required=True, dest=SCMATCH_URL,
                        help="scMatch git repo url")
    parser.add_argument('--cellranger', required=True, dest=CELLRANGER_VERSION,
                        help="cellranger version string")
    parser.add_argument('--gitrepo', required=True, dest=GIT_REPO,
                        help="git repo URL")
    parser.add_argument('--githash', required=True, dest=GIT_COMMIT,
                        help="git commit hash")
    #parser.add_argument('-j', required=True, dest=CFG,
    #                    help="Config file")
    args = parser.parse_args()
    return vars(args)


def fill_template(context, plot_list, template_path, output):
    if os.path.isfile(template_path):
        template = get_jinja_template(template_path)
        with open(output, 'w') as fout:
            fout.write(template.render(context,
                                       kmeans_clust = plot_list))
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
    #j = json.load(open(arg_dict[CFG]))

    # Make the dictionaries to go into context
    versions_dict = {"cellranger_version" : arg_dict[CELLRANGER_VERSION],
                     "scmatch_hash" : arg_dict[SCMATCH_HASH],
                     "scmatch_url" : arg_dict[SCMATCH_URL],
                     "git_repo" : arg_dict[GIT_REPO],
                     "git_commit" : arg_dict[GIT_COMMIT]}
    graph_dict = {
        "celltype_clust" : arg_dict[SCMATCH],
        "graph_clust" : arg_dict[GRAPH]
    }
    #kmeans_dict = {"kmeans_clust" : arg_dict[KMEANS]}
    kmeans_list = arg_dict[KMEANS]
    name_dict = {
        #"output_report_filename" : arg_dict[OUTPUT],
        "input_fastq_filename" : arg_dict[INPUT],
        "sample_name" : arg_dict[SAMPLENAME]
    }
    # make the context dictionary
    context = {}
    context.update(versions_dict)
    context.update(graph_dict)
    #context.update(kmeans_dict)
    context.update(name_dict)
    #context.update(arg_dict)
    #context.update(j)

    # fill and write the completed report:
    fill_template(context, kmeans_list, input_template_path, output_file)
