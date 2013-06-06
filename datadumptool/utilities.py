# utilities.py
# A set of utility methods used by the TrustForge Harness script.
# written by Peter Gebhard

import os, sys, csv, subprocess, zipfile, logging, cPickle, re
from datetime import datetime
from operator import itemgetter
import pymongo
from pygraph.classes.digraph import digraph
from pygraph.classes.graph import graph
from pygraph.readwrite.dot import write as dotwrite
from pygraphviz import *
import networkx as nx

logger = logging.getLogger('datadump-tool')

def pickScenario():
    scenarios = printScenarioList()
    try:
        scenarioNum = input('Enter scenario number: ')
    except SyntaxError:
        scenarioNum = -1
    while scenarioNum not in range(0, len(scenarios)):
        print 'Please enter a valid scenario number.'
        try:
            scenarioNum = input('Enter scenario number: ')
        except SyntaxError:
            scenarioNum = -1
    return scenarios[scenarioNum]


def pickResultSet():
    resultsSets = printResultsSetList()
    if resultsSets != None:
        try:
            resultsNum = input('Enter results set number (-1 to skip): ')
        except SyntaxError:
            resultsNum = -2

        # Skip with results set to None
        if resultsNum == -1:
            results = None
            print 'Skipping results set processing.'
        else:
            while resultsNum not in range(0, len(resultsSets)):
                print 'Please enter a valid results set number.'
                try:
                    resultsNum = input('Enter results set number (-1 to skip): ')
                except SyntaxError:
                    resultsNum = -2

                # Skip by breaking from while loop with results set to None
                if resultsNum == -1:
                    results = None
                    print 'Skipping results set processing.'
                    break
            if resultsNum >= 0:
                results = resultsSets[resultsNum]
    else:
        results = None

    return results


def pickOutputType():
    print 'What type of output do you want?'
    print '( 0 ) User reputation only'
    print '( 1 ) Component reputation only'
    print '( 2 ) Both User and Component reputation'
    try:
        outputType = input('Enter output type: ')
        # Default to outputType of 0 if none of the proper choices are entered
        if outputType not in range(0,3):
            print '(Defaulting to User reputation only)'
            outputType = 0
    except SyntaxError:
        # Default to outputType of 0 if there's an input error
        print '(Defaulting to User reputation only)'
        outputType = 0

    return outputType


def cleanup():
    User.query.remove()
    Component.query.remove()


def createCSVWriter(file, conn):
    ulist = conn.list_users()
    ulist.sort()
    clist = conn.list_components_with_revision(current_only=False)
    clist.sort()
    fields = ulist + clist
    writer = csv.DictWriter(file, fields)
    writer.writeheader()
    return writer


def printUserReputationCSV(csvwriter, conn):
    csvwriter.writerow(dict((u, User.get_by_name(u).reputation) for u in conn.list_users()))


def printUserReputation(ulist):
    ulist.sort()
    return '\n'.join(["user: %s rep: %s" % (u, User.get_by_name(u).reputation) for u in ulist])


def printCompReputation(clist):
    clist.sort()
    return '\n'.join(["comp: %s rev: %s rep: %s" % (c.rpartition('_')[0], c.rpartition('_')[2],
        Component.get_by_name(name=c.rpartition('_')[0], revision=int(c.rpartition('_')[2])).reputation) for c in clist])


def printUserRepAndTestsCSV():
    loadDatadump(dump)

    f = open(dump + '_userrep_and_tests.csv', 'w')

    trustmodel.init_model()
    conn = ModelInterface()

    users = {User.get_all(active_only=False):[]}

    for component in Component.get_all():
        for author in component.authors:
            users[author].append(component.get_tests())

    for user in users:
        f.write(user.name + ',' + user.reputation + ',')
        # TODO - Complete this method!


def printScenarioList():
    # Get a list of the scenario files in the 'scenarios' directory
    scenarios = os.listdir('scenarios')

    if len(scenarios) == 0:
        raise RuntimeError('There are no scenarios available to execute!')

    print 'Please choose a scenario (by number):'

    # Remove .pyc files, the .py extension, and __init__ before we print list
    scenarios = [s.split('.')[0] for s in scenarios if s[-2:] == 'py' and s[:8] != '__init__']

    # Print list of scenarios
    i = 0
    for s in scenarios:
        print '(', i, ') ', s
        i += 1

    return scenarios


def printResultsSetList():
    # Get a list of the results sets in the 'parsers/resultsSets' directory
    resultsSets = os.listdir('parsers/resultsSets')
    resultsSets.remove('placeholder.txt')

    if len(resultsSets) == 0:
        print 'No results sets to choose from.'
        return None

    print 'Please choose a results set (by number):'

    i = 0
    for r in resultsSets:
        print '(', i, ') ', r
        i += 1

    return resultsSets


def printTopLevelCompsByScore():
    top_comps = getTopLevelComps()

    top_comps = sorted(top_comps, key=lambda comp: getMaxTestScore(comp), reverse=True)

    for comp in top_comps:
        print comp.name + ", authors: " + str(comp.usernames) + ", score: " + str(getMaxTestScore(comp))
        print " "


def getMaxTestScore(comp):
    return max(comp.tests, key=lambda test: test.score)


def userCompDict():
    trustmodel.init_model()

    uc_dict = {}.fromkeys(User.get_all(active_only=False))

    for key in uc_dict.iterkeys():
        uc_dict[key] = []
        #for comp in Component.get_by_author(key.name):
        #   uc_dict[key].append(comp)

    for comp in Component.get_all():
        for user in comp.authors:
            uc_dict[user].append(comp)

    return uc_dict


def pickleDatadumpContents(dump, dumpDir='../../../datadumps/'):
    loadDatadump(dump, dumpDir)

    userPkl = open(dumpDir + dump + '_User.pkl', 'wb')
    compPkl = open(dumpDir + dump + '_Component.pkl', 'wb')

    trustmodel.init_model()

    users = []
    comps = []

    for user in User.get_all(active_only=False):
        users.append((user.name, user.reputation))

    for component in Component.get_all():
        comps.append((component.name, component.revision, component.reputation))

    cPickle.dump(users, userPkl)
    cPickle.dump(comps, compPkl)

    userPkl.close()
    compPkl.close()


def unpickleDatadumpContents(dump, dumpDir='../../../datadumps/'):
    userPkl = open(dumpDir + dump + '_User.pkl', 'rb')
    compPkl = open(dumpDir + dump + '_Component.pkl', 'rb')

    users = cPickle.load(userPkl)
    comps = cPickle.load(compPkl)

    userPkl.close()
    compPkl.close()

    # Sort lists before returning
    users.sort(key=itemgetter(0))
    comps.sort(key=itemgetter(0,1))

    return (users, comps)


def compareDatadumpPickles(pklOne, pklTwo, pklDir='../../../datadumps/'):
    userPklOne = open(pklDir + pklOne + '_User.pkl', 'rb')
    compPklOne = open(pklDir + pklOne + '_Component.pkl', 'rb')
    userPklTwo = open(pklDir + pklTwo + '_User.pkl', 'rb')
    compPklTwo = open(pklDir + pklTwo + '_Component.pkl', 'rb')

    usersOne = cPickle.load(userPklOne)
    compsOne = cPickle.load(compPklOne)
    usersTwo = cPickle.load(userPklTwo)
    compsTwo = cPickle.load(compPklTwo)

    userPklOne.close()
    compPklOne.close()
    userPklTwo.close()
    compPklTwo.close()

    # TODO - Write comparisons here


def loadDatadump(dump, dumpDir='../../../datadumps/'):
    if dump in os.listdir(dumpDir):
        restoreDatadump(dumpDir + dump)
    else:
        extractDatadumpZip(dumpDir + dump, dumpDir)
        restoreDatadump(dumpDir + dump)


def extractDatadumpZip(dump, dumpDir='../../../datadumps/'):
    with zipfile.ZipFile(dump + '.zip', 'r') as myzip:
        myzip.extractall(dumpDir)


def restoreDatadump(dump):
    # Find name of the database stored in the dump
    dumpDatabase = os.listdir(dump)[0]

    # Rename existing dumpDatabase in Mongo, if it exists
    mongo = pymongo.Connection()
    dbs = mongo.database_names()

    if dumpDatabase in dbs:
        mongo.copy_database(dumpDatabase,
            dumpDatabase + '_' + str(datetime.now()).replace(' ','_').replace('.','_'))
        mongo.drop_database(dumpDatabase)

    # Restore dumpName to Mongo
    subprocess.check_call(['mongorestore',dump])


def clearTFMongoDatabases():
    mongo = pymongo.Connection()
    [mongo.drop_database(db) for db in mongo.database_names() if db.startswith('dump')]


def constructGraph(conn):
    gr = digraph()

    # Add components (with revision numbers) to the graph
    comps = conn.list_components_with_revision(current_only=False)
    gr.add_nodes(comps)

    # Add edges (with revision numbers) between components and their subcomponents to the graph
    cedges = conn.list_edges_with_revision(source_current=True, target_current=False)
    for edge in cedges:
        gr.add_edge(edge)

    #logger.debug(gr)

    return gr


def getTopLevelComps():
    trustmodel.init_model()
    top_comps = []
    for comp in Component.get_all():
        if isTopLevelCompName(comp.name):
            top_comps.append(comp)
    return top_comps


def getSortedUsersByRep():
    trustmodel.init_model()
    return sorted(User.get_all(active_only=False), key=lambda user: user.reputation, reverse=True)


def isTopLevelCompName(name):
    top = re.compile('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')
    return top.match(name) is not None


def getUserContribType(username):
    userComps = Component.get_by_author(username)
    topLevel = 0
    leafs = 0
    dualFlag = False
    for comp in userComps:
        if isTopLevelCompName(comp.name):
            topLevel += 1
        else:
            leafs += 1

    if topLevel > leafs:
        type = 'integrator'
    elif leafs > topLevel:
        type = 'designer'
    elif topLevel > 0 and leafs == topLevel:
        type = 'integrator'
    else:
        type = 'non-contributor'

    if topLevel > 0 and leafs > 0:
        dualFlag = True

    return (type, dualFlag)


def constructAuthorGraph(comps):
    gr = AGraph(strict=False)
    gr.node_attr.update(color='red')
    gr.edge_attr.update(color='blue')

    for comp in comps:
        edges = set()
        userCount = len(comp.usernames)

        # Build set of component author edges for the component
        for i in range(userCount):
            for j in range(i+1, userCount):
                edges.add((comp.usernames[i], comp.usernames[j]))
        edges = list(edges)

        # Add component authors to the graph
        for author in comp.authors:
            if not gr.has_node(author.name):
                lab = '(' + author.name + ', rep: ' + str(author.reputation) + ')'
                if len(comp.authors) == 1:
                    lab += ', (comp: ' + comp.name + ', rep: ' + str(comp.reputation) + ')'
                gr.add_node(author.name, label=lab)

        # Add edges between component authors
        for edge in edges:
            gr.add_edge(edge[0], edge[1], key=comp, label='(' + comp.name + ', rep: ' + str(comp.reputation) + ')')
            #gr.add_edge(edge[0], edge[1], label='testing')

    #logger.debug(gr)
    #return gr

    timeStr = str(datetime.now()).replace(' ','_').replace('.','_').replace(':','-')
    gr.write('author_graph_' + timeStr + '.dot')


def constructUserGraph(comps):
    gr = nx.Graph()

    for comp in comps:
        edges = set()
        userCount = len(comp.usernames)

        # Build set of component author edges for the component
        for i in range(userCount):
            for j in range(i+1, userCount):
                edges.add((comp.usernames[i], comp.usernames[j]))
        edges = list(edges)

        # Add component authors to the graph
        for author in comp.authors:
            if not gr.has_node(author.name):
                lab = '(' + author.name + ', rep: ' + str(author.reputation) + ')'
                if len(comp.authors) == 1:
                    lab += ', (comp: ' + comp.name + ', rep: ' + str(comp.reputation) + ')'
                gr.add_node(author.name, label=lab)

        # Add edges between component authors
        for edge in edges:
            gr.add_edge(edge[0], edge[1], key=comp, label='(' + comp.name + ', rep: ' + str(comp.reputation) + ')')

    #logger.debug(gr)
    return gr


def outputDotFile(conn=None, dotDir='./results/'):
    if conn is None:
        logger.info('Initiating storage connection...')
        trustmodel.init_model()
        conn = ModelInterface()

    timeStr = str(datetime.now()).replace(' ','_').replace('.','_').replace(':','-')
    dotFile = open(dotDir + 'dot_graph_' + timeStr + '.dot', 'wb')
    dotFile.write(dotwrite(constructGraph(conn)))
    dotFile.close()

