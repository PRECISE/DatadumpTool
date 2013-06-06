# datadump_utils.py
# This script provides utility methods for processing a datadump, restoring a dump, and
#  outputting relevant statistics.
# written by Peter Gebhard

import logging, os
#TODO: from fabric.api import *

import utilities
import stats

import pygraphviz as pgv

def getStats(dump=None):
    logger = logging.getLogger('datadump-tool')
    # INFO will get rid of debugging prints; WARNING suppresses even more messages
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    if dump is None:
        logger.info('Asking user for datadump choice...')
        dump = pickDatadump()

    logger.info('Loading ' + dump + '...')
    utilities.loadDatadump(dump, dumpDir='./')

    logger.info('Initiating storage connection...')
    trustmodel.init_model()
    conn = ModelInterface()

    logger.info('Constructing graph of ' + dump + ' from MongoDB contents...')
    pgvGraph = pgv.AGraph(strict=False, directed=True)
    pgvGraph.graph_attr['label'] = dump
    pgvGraph.graph_attr['packMode'] = 'node'
    pgvGraph.node_attr['shape'] = 'circle'
    pgvGraph.edge_attr['color'] = 'red'

    comps = conn.list_components_with_revision(current_only=False)
    pgvGraph.add_nodes_from(comps)

    cedges = conn.list_edges_with_revision(False, False)
    for edge in cedges:
        pgvGraph.add_edge(edge[0],edge[1])

    pgvGraph.layout(prog='dot')

    # Draw as PNG
    logger.info('Drawing PNG graph of ' + dump + '...')
    pgvGraph.draw(dump + '_output.png')

    # Write dot-file
    logger.info('Writing graph dot-file of ' + dump + '...')
    pgvGraph.write(dump + '_output.dot')

    logger.info('Generating statistics for ' + dump + '...')
    stat = stats.TFStats(logger=logger)
    stat.output(dump + "_stats")

    logger.info("DONE")


def countDatadumpComponentEdges(dump):
    utilities.loadDatadump(dump, dumpDir='./')
    trustmodel.init_model()

    return len(ModelInterface().list_edges_with_revision(source_current=True, target_current=False))


def countDatadumpTests(dump):
    utilities.loadDatadump(dump, dumpDir='./')
    trustmodel.init_model()

    tests = 0

    for component in Component.get_all():
        tests += len(component.get_tests())

    return tests


def printDatadumpsList():
    if (not os.getcwd().endswith('datadumps')):
        raise RuntimeError("You're trying to run this script outside the datadumps \
            directory.  Please try running it from that directory.")

    # Get a list of the datadump zip files in the 'datadumps' directory
    datadumps = [d.split('.')[0] for d in os.listdir('.') if d[-3:] == 'zip']

    if len(datadumps) == 0:
        print 'No datadumps to choose from.'
        return None

    print 'Please choose a datadump (by number):'

    i = 0
    for d in datadumps:
        print '(', i, ') ', d
        i += 1

    return datadumps


def pickDatadump():
    datadumps = printDatadumpsList()
    try:
        dumpNum = input('Enter datadump number: ')
    except SyntaxError:
        dumpNum = -1
    while dumpNum not in range(0, len(datadumps)):
        print 'Please enter a valid datadump number.'
        try:
            dumpNum = input('Enter datadump number: ')
        except SyntaxError:
            dumpNum = -1
    return datadumps[dumpNum]


if __name__ == "__main__":
    getStats()
