#!/usr/bin/env pypy
"""pypy only merge watson and crick calls to custom format"""
import argparse
import gzip

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Process input files')
    parser.add_argument('-w', '--watson', type=str, default=None,
                        help='watson (top strand) .vcf file input.')
    parser.add_argument('-c', '--crick', type=str, default=None,
                        help='crick (bottom strand) .vcf file input.')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='output custom tabular format')
    args = parser.parse_args()
    return args

def merge_line(watson_line,crick_line):
    """merge watson and crick output"""
    out_line = watson_line[:2] + [watson_line[3]] + [watson_line[4][:-3]] + [crick_line[4][:-3]] + ['']*len(watson_line[9:])
    AD_index = watson_line[8].split(':').index('AD')
    watson_nt_index = watson_line[4][:-4].split(',')
    crick_nt_index = crick_line[4][:-4].split(',')
    for nt in 'ACGT':
        nt_pos_watson = None
        nt_pos_crick = None
        if nt == watson_line[3]:
            nt_pos_watson = 0
            nt_pos_crick = 0
        if nt in watson_nt_index:
            nt_pos_watson = watson_nt_index.index(nt) + 1
        if nt in crick_nt_index:
            nt_pos_crick = crick_nt_index.index(nt) + 1
        for index,(w_value,c_value) in enumerate(zip(watson_line[9:],crick_line[9:])):
            try:
                watson_obs = w_value.split(':')[AD_index].split(',')[nt_pos_watson]
            except TypeError:
                watson_obs = 0
            try:
                crick_obs = c_value.split(':')[AD_index].split(',')[nt_pos_crick]
            except TypeError:
                crick_obs = 0
            out_line[index+5] += '%s,%s:' % (watson_obs, crick_obs)
    return '\t'.join([e.rstrip(':') for e in out_line]) + '\n'

def merge(args):
    """"merge watson and crick calls"""
    watson_handle = gzip.open(args.watson)
    crick_handle = gzip.open(args.crick)
    read_watson = True
    read_crick = True
    #TODO: define output header
    output = gzip.open(args.output, 'w')
    count = 0
    while True:
        if read_watson:
            watson_line = watson_handle.readline()
        if read_crick:
            crick_line = crick_handle.readline()
        if watson_line.startswith('#CHROM'):
            watson_header = watson_line[:-1].split('\t')
            read_watson = False
        if crick_line.startswith('#CHROM'):
            crick_header = crick_line[:-1].split('\t')
            read_crick = False
        if read_watson == False and read_crick == False:
            break
    read_watson = True
    read_crick = True
    while True:
        if read_watson:
            while True:
                try:
                    watson_line = watson_handle.next()[:-1].split('\t')
                except StopIteration:
                    break
                if 'INDEL' not in watson_line:
                    break
        if read_crick:
            while True:
                try:
                    crick_line = crick_handle.readline()[:-1].split('\t')
                except StopIteration:
                    break
                if 'INDEL' not in crick_line:
                    break
        if watson_line[0] == crick_line[0]:
            if watson_line[1] == crick_line[1]:
                count += 1
                if not count % 1000000:
                    print 'processed %s lines' % count
                output_line = merge_line(watson_line, crick_line)
                output.write(output_line)
                #start reading both lines again.
                read_watson = True
                read_crick = True
            elif int(watson_line[1]) > int(crick_line[1]):
                read_watson = False
                read_crick = True
            else:
                read_crick = False
                read_watson = True
        elif watson_line[0] == '' or crick_line[0] == '':
            break
        elif int(watson_line[0]) > int(crick_line[0]):
            read_watson = False
            read_crick = True
        else:
            read_crick = False
            read_watson = True
    output.close()
def main():
    """Main function loop"""
    args = parse_args()
    merge(args)
    
    
    
if __name__ == '__main__':
    main()