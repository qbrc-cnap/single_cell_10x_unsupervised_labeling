#! /usr/bin/python3

import subprocess as sp
import argparse
import re
import sys
import os
import signal


# This sets a timeout on the fastqValidator
TIMEOUT = 3600 # seconds


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    '''
    Can add other behaviors here if desired.  This function
    is hit if the timeout occurs
    '''
    raise TimeoutException('')


def run_cmd(cmd, return_stderr=False, set_timeout=False):
    '''
    Runs a command through the shell
    '''
    if set_timeout:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT)

    p = sp.Popen(cmd, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)
    try:
        stdout, stderr = p.communicate()
        if return_stderr:
            return (p.returncode, stderr.decode('utf-8'))
        return (p.returncode, stdout.decode('utf-8'))
    except TimeoutException as ex:
        return (1, 'A process is taking unusually long to complete.  It is likely that the FASTQ file is corrupted.  The process run was %s' % cmd)


def check_matched_pairs(indices, fastqs):
    '''Checks that there is a matching FASTQ with indices.'''
    suffix = ".fastq.gz"
    indices_base = [re.sub(suffix, "", i) for i in indices]
    indices_base = [re.sub("_I", "_", i) for i in indices_base]
    fastqs_base = [re.sub(suffix, "", f) for f in fastqs]
    fastqs_base = [re.sub("_R", "_", f) for f in fastqs_base]
    return len(set(indices_base).difference(set(fastqs_base))) == 0


def check_fastq_format(f):
    '''
    Runs the fastQValidator on the fastq file
    IF the file is invalid, the return code is 1 and
    the error goes to stdout.  If OK, then return code is zero.
    '''
    cmd = 'fastQValidator --file %s' % f
    rc, stdout_string = run_cmd(cmd, set_timeout=True)
    if rc == 1:
        return [stdout_string]
    return []

def check_gzip_format(f):
    '''
    gzip -t <file> has return code zero if OK
    if not, returncode is 1 and error is printed to stderr
    '''
    cmd = 'gzip -t %s' % f
    rc, stderr_string = run_cmd(cmd, return_stderr=True)
    if rc == 1:
        return [stderr_string]
    return []


def catch_very_long_reads(f, N=100, L=300):
    '''
    In case we get non-illumina reads, they will not exceed some threshold (e.g. 300bp)
    '''
    err_list = []
    zcat_cmd = 'zcat %s | head -%d' % (f, 4*N)
    rc, stdout = run_cmd(zcat_cmd)
    lines = stdout.split('\n')
        
    # iterate through the sampled sequences.  
    # We don't want to dump a ton of long sequences, so if we encounter
    # ANY in our sample, save an error message and exit the loop.
    # Thus, at most one error per fastq.
    i = 1
    while i < len(lines):
        if len(lines[i]) > L:
            return ['Fastq file (%s) had a read of length %d, '
                'which is too long for a typical Illumina read.  Failing file.' % (f, len(lines[i]))]
        i += 4
    return []


def main():
    '''Checks for valid FASTQs.'''
    # Arg parsing
    parser = argparse.ArgumentParser(description="Check for valid FASTQs.")
    parser.add_argument("-i", "--indices", metavar="INDICES", nargs="+",
                        help="Index FASTQ files")
    parser.add_argument("-f", "--fastqs", metavar="FASTQS", nargs="+",
                        help="FASTQ sequencing files")
    args = parser.parse_args()
    err_list = []
    if not check_matched_pairs(args.indices, args.fastqs):
        e = "There was an issue with matching your index FASTQs to your sequencing FASTQs."
        err_list.append(e)

    for fastq_filepath in args.indices + args.fastqs:
        # check that fastq in gzip:
        err_list.extend(check_gzip_format(fastq_filepath))

        # check the fastq format
        err_list.extend(check_fastq_format(fastq_filepath))

        # check that read lengths are consistent with Illumina:
        err_list.extend(catch_very_long_reads(fastq_filepath))
    
    if len(err_list) > 0:
        sys.stderr.write('#####'.join(err_list)) # the 5-hash delimiter since some stderr messages can be multiline
        sys.exit(1) # need this to trigger Cromwell to fail


if __name__ == "__main__":
    main()
