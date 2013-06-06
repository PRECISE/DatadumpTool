# datadump_tool.py
# This script provides tools for generating, deploying, and querying TrustForge datadumps.
# written by Peter Gebhard, January 2013

import logging, cmd, numpy

import networkx as nx

import datadump_utils
from stats import Stats
import utilities

# TODO: add methods for: generating mongo dumps, restoring mongo dumps (locally and
#   remotely deployed), making useful Mongo queries, etc.

class DatadumpTool(cmd.Cmd):

    prompt = '(datadump-tool) '
    dump = None
    stats = None

    def do_load_dump(self, line):
        "Load a datadump to the local running Mongo instance"
        self.dump = datadump_utils.pickDatadump()
        self.prompt = '(datadump-tool - ' + self.dump + ') '
        utilities.loadDatadump(self.dump, dumpDir='./')


    def do_deploy_dump(self, line):
        "Deploy a datadump to AWS"
        print 'Not yet implemented.'


    def do_generate_dump(self, line):
        "Generate a dump of the loaded database"
        print 'Not yet implemented.'


    def do_stats(self, line):
        "Calculate statistics on a datadump"

        dump = line
        if len(dump) == 0:
            dump = None

        if dump is None:
            if self.dump is None:
                self.do_load_dump(line)
            dump = self.dump
        else:
            if dump != self.dump:
                try:
                    utilities.loadDatadump(dump, dumpDir='./')
                except IOError, OSError:
                    print "Error: Could not find dump '" + dump + "'."
                    return
                oldDump = self.dump
                self.dump = dump
                try:
                    if self.stats is None:
                        self.stats = Stats(dump + "_stats")
                    self.stats.output_all()
                except:
                    print "Error: Failed to complete stats output."
                if oldDump is not None:
                    utilities.loadDatadump(oldDump, dumpDir='./')
                    self.dump = oldDump
                self.prompt = '(datadump-tool - ' + self.dump + ') '
                return

        try:
            if self.stats is None:
                self.stats = Stats(dump + "_stats")
            self.stats.output_all()
        except:
            print "Error: Failed to complete stats output."


    def do_clear_mongo(self, line):
        "Drop all old databases from Mongo"
        utilities.clearMongoDatabases()


    def do_print_root_node_data(self, line):
        "Find all of the root, top-level nodes in the graph"
        utilities.printTopLevelCompsByScore()


    def do_print_authors(self, line):
        "Print map of authors extracted from the node data"
        comps = sorted(utilities.getTopLevelComps(), key=lambda comp: utilities.getMaxTestScore(comp), reverse=True)
        # Only graph top 1% of top-level components (by test score)
        utilities.constructAuthorGraph(comps[0:int(0.01*len(comps))])


    def do_find_leaf_nodes(self, line):
        "Find all of the leaf nodes in the graph"
        for comp in Component.get_all():
            if (not utilities.isTopLevelCompName(comp.name) and comp.submit):
                print "Submitted Leaf PROBLEM: " + str(comp)


    def do_find_root_nodes(self, line):
        "Find all of the root, top-level nodes in the graph"
        for comp in Component.get_all():
            if utilities.isTopLevelCompName(comp.name) and len(comp.subcomponents) == 0:
                print "Top-level comp without subcomps PROBLEM: " + str(comp)


    def do_calc_graph_scc(self, line):
        "Calculate the strongly connected components in the graph"
        G = utilities.constructUserGraph(Component.get_all())
        scc = nx.strongly_connected_components(G)

        teams = dict()
        counter = 0
        userCount = 0
        for c in scc:
            print " "
            print "Cluster " + str(counter) + ", " + str(len(c)) + " users:"

            repList = []
            for user in c:
                repList.append(User.get_by_name(user).reputation)
                teams[user] = counter
                type = utilities.getUserContribType(user)
                print "  " + str(User.get_by_name(user)) + "  type: " + type[0] + " dual: " + str(type[1])

            print "min : " + str(numpy.min(repList))
            print "max : " + str(numpy.max(repList))
            print "mean : " + str(numpy.mean(repList))
            print "median : " + str(numpy.median(repList))
            print "var : " + str(numpy.var(repList))

            counter += 1
            userCount += len(c)

        #print "Total users counted: " + str(userCount)

        unowned = 0
        singleTeam = 0
        multiTeam = 0
        for comp in Component.get_all():
            compTeams = []
            for name in comp.usernames:
                if teams[name] not in compTeams:
                    compTeams.append(teams[name])
            if len(compTeams) == 0:
                print "Unowned component: " + str(comp)
                unowned += 1
            elif len(compTeams) == 1:
                singleTeam += 1
            else:
                print "Multi-team component: " + str(comp)
                multiTeam += 1


    def do_show_user_types(self, line):
        "Show user type statistics"
        if self.dump is None:
            print "Please use load_dump first."
            return
        if self.stats is None:
            self.stats = Stats(self.dump + "_stats")
        self.stats.output_user_types()


    def do_exit(self, line):
        "Exit from the shell"
        print 'Goodbye!'
        return True


if __name__ == "__main__":
    DatadumpTool().cmdloop()
