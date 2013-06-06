# stats.py
# A set of statistic methods used for datadump analysis.
# written by Peter Gebhard

import logging, unittest, numpy, scipy.stats, os, csv, glob

import utilities

from pylab import *

class Stats(object):
    """ A parser of the VehicleForge Requirements (in their JSON format) """

    def __init__(self, outputDir, users=None, comps=None, logger=None):
        """ Initialize.

        Args:
            outputDir (str): directory containing the statistical output
        """
        if logger is None:
            self.logger = logging.getLogger('datadump-tool')
        else:
            self.logger = logger

        self.outputDir = outputDir
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)

        if users is not None:
            self.users = users
        else:
            self.users = self._getUsers()

        if comps is not None:
            self.comps = comps
        else:
            self.comps = self._getComps()

        self.ucDict = utilities.userCompDict()
        self.contribSet = set()

        self.in_degree = {}.fromkeys(self._getComps())
        self.out_degree = {}.fromkeys(self._getComps())

        # Store the in-degree of a component
        for key in self.in_degree.iterkeys():
            self.in_degree[key] = key.in_degree

        # Store the out-degree of a component
        for key in self.out_degree.iterkeys():
            self.out_degree[key] = key.out_degree


    def output_all(self):
        # Cleanup the directory, or, create a new directory if none exists

        #TODO: change to use cleanup method
        if os.path.exists(self.outputDir):
            files = ['user_rep', 'user_rep_changes', 'user_contrib_rep', 'user_designs_vs_comps',
                     'comp_rep', 'comp_subm_rep', 'comp_nonsubm_rep',
                     'comp_in_degree', 'comp_out_degree', 'comp_rev_changes', 'stats',
                     'comp', 'user']
            filetypes = ['png', 'pdf', 'eps', 'csv', 'txt']
            for file in files:
                for filetype in filetypes:
                    if os.path.exists(self.outputDir + '/' + file + '.' + filetype):
                        os.remove(self.outputDir + '/' + file + '.' + filetype)

            for file in glob.glob(self.outputDir + '/user_comp_rep_*'):
                os.remove(file)
        else:
            os.mkdir(self.outputDir)

        statFile = open(self.outputDir + '/stats.txt', 'w')
        compCSVWriter = csv.DictWriter(open(self.outputDir + '/comp.csv', 'w'),
            ['component', 'reputation', 'tests', 'in_degree', 'out_degree'])
        compCSVWriter.writeheader()
        userCSVWriter = csv.DictWriter(open(self.outputDir + '/user.csv', 'w'),
            ['user', 'reputation', 'components', 'submitted'])
        userCSVWriter.writeheader()


        userC = self.userCounts()
        statFile.write("-- Overall User Counts --\n")
        statFile.write("total: %s\n" % userC[0])
        statFile.write("contributors: %s\n" % userC[1])


        userRS = self.userRepStats()
        statFile.write("\n-- User Reputation Statistics --\n")
        statFile.write("max rep algo iterations: %s\n" % userRS[0])
        statFile.write("min: %s\n" % userRS[3])
        statFile.write("max: %s\n" % userRS[4])
        statFile.write("mean: %s\n" % userRS[5])
        statFile.write("median: %s\n" % userRS[6])
        statFile.write("variance: %s\n" % userRS[7])
        statFile.write("\n")
        statFile.write("min change: %s\n" % userRS[9])
        statFile.write("max change: %s\n" % userRS[10])
        statFile.write("mean change: %s\n" % userRS[11])
        statFile.write("median change: %s\n" % userRS[12])
        statFile.write("variance change: %s\n" % userRS[13])

        for row in userRS[1]:
            userCSVWriter.writerow(row)

        figure()
        plot(userRS[2])
        xlabel('User')
        ylabel('Reputation')
        title('User Reputation')
        grid(True)
        self._saveTFFig("user_rep.png")

        figure()
        plot(userRS[8])
        xlabel('User')
        ylabel('Reputation')
        title('User Reputation Changes between Iterations')
        grid(True)
        self._saveTFFig("user_rep_changes.png")


        userRCS = self.userRepContribStats()
        statFile.write("\n-- Contributor User Reputation Statistics --\n")
        statFile.write("min: %s\n" % userRCS[1])
        statFile.write("max: %s\n" % userRCS[2])
        statFile.write("mean: %s\n" % userRCS[3])
        statFile.write("median: %s\n" % userRCS[4])
        statFile.write("variance: %s\n" % userRCS[5])

        figure()
        plot(userRCS[0])
        xlabel('User')
        ylabel('Reputation')
        grid(True)
        self._saveTFFig("user_contrib_rep.png")


        statFile.write("\n-- User-Component Reputation Statistics --\n")
        for user in self.users:
            if len(self.ucDict[user]) > 0:
                userCRS = self.userComponentsRepStats(user)
                statFile.write(str(user))
                statFile.write("  count: %s" % len(userCRS[0]))
                statFile.write("  min: %s" % userCRS[1])
                statFile.write("  max: %s" % userCRS[2])
                statFile.write("  mean: %s" % userCRS[3])
                statFile.write("  median: %s" % userCRS[4])
                statFile.write("  variance: %s" % userCRS[5])
                statFile.write("  submitted ratio: %s\n" % userCRS[6])


        ucReps = self.userCompReps()
        for user in ucReps:
            figure()
            plot(user[2])
            xlabel('User ' + user[0] + ' - Reputation: ' + str(user[1]) + ' - Components: ' + str(len(user[2])))
            ylabel('Component Reputation')
            grid(True)
            self._saveTFFig("user_comp_rep_"+user[0]+".png")


        result = self.userDesignsVsComponent()
        figure()
        scatter(result[0], result[1])
        xlabel('General Components')
        ylabel('Top-Level Components (Designs)')
        grid(True)
        self._saveTFFig("user_designs_vs_comps.png")



        compC = self.compCounts()
        statFile.write("\n-- Overall Component Counts --\n")
        statFile.write("total: %s\n" % compC[0])
        statFile.write("submitted: %s\n" % compC[1])
        statFile.write("unsubmitted: %s\n" % compC[5])
        statFile.write("unused: %s\n" % compC[6])
        statFile.write("tested: %s\n" % compC[2])
        statFile.write("multi-revisioned: %s\n" % compC[7])

        figure()
        plot(sorted(compC[3].values()))
        xlabel('Component')
        ylabel('In-Degree')
        yscale('log')
        title('Component In-Degree')
        grid(True)
        self._saveTFFig("comp_in_degree.png")

        figure()
        plot(sorted(compC[4].values()))
        xlabel('Component')
        ylabel('Out-Degree')
        yscale('log')
        title('Component Out-Degree')
        grid(True)
        self._saveTFFig("comp_out_degree.png")


        compRS = self.compRepStats()
        statFile.write("\n-- Component Reputation Stats --\n")
        statFile.write("max rep algo iterations: %s\n" % compRS[0])
        statFile.write("min: %s\n" % compRS[3])
        statFile.write("max: %s\n" % compRS[4])
        statFile.write("mean: %s\n" % compRS[5])
        statFile.write("median: %s\n" % compRS[6])
        statFile.write("variance: %s\n" % compRS[7])
        statFile.write("reputation & in-degree Pearson: %s\n" % str(compRS[8]))
        statFile.write("reputation & out-degree Pearson: %s\n" % str(compRS[9]))

        for row in compRS[1]:
            compCSVWriter.writerow(row)

        figure()
        plot(compRS[2])
        xlabel('Component')
        ylabel('Reputation')
        title('Component Reputation')
        grid(True)
        self._saveTFFig("comp_rep.png")


        compTLS = self.compTopLevelStats()
        statFile.write("\n-- Top-Level Component Stats --\n")
        perc = int(0.05 * len(compTLS[0]))
        for i in range(perc):
            statFile.write("%s:\n" % compTLS[0][i])
            for author in compTLS[0][i].authors:
                statFile.write("    %s\n" % author)


        compRSS = self.compRepSubmittedStats()
        statFile.write("\n-- Submitted & Non-Submitted Component Reputation Statistics --\n")
        statFile.write("min (Submitted): %s\n" % compRSS[1])
        statFile.write("max (Submitted): %s\n" % compRSS[2])
        statFile.write("mean (Submitted): %s\n" % compRSS[3])
        statFile.write("median (Submitted): %s\n" % compRSS[4])
        statFile.write("variance (Submitted): %s\n" % compRSS[5])
        statFile.write("\n")

        figure()
        plot(compRSS[0])
        xlabel('Component')
        ylabel('Reputation')
        grid(True)
        self._saveTFFig("comp_subm_rep.png")

        statFile.write("min (Non-Submitted): %s\n" % compRSS[7])
        statFile.write("max (Non-Submitted): %s\n" % compRSS[8])
        statFile.write("mean (Non-Submitted): %s\n" % compRSS[9])
        statFile.write("median (Non-Submitted): %s\n" % compRSS[10])
        statFile.write("variance (Non-Submitted): %s\n" % compRSS[11])

        figure()
        plot(compRSS[6])
        xlabel('Component')
        ylabel('Reputation')
        title('Non-Submitted Component Reputation')
        grid(True)
        self._saveTFFig("comp_nonsubm_rep.png")


        compRCS = self.compRevChangeStats()
        statFile.write("\n-- Component Revision Change Statistics --\n")
        statFile.write("- Reputation Changes between first and latest revision -\n")
        statFile.write("min: %s\n" % compRCS[1])
        statFile.write("max: %s\n" % compRCS[2])
        statFile.write("mean: %s\n" % compRCS[3])
        statFile.write("median: %s\n" % compRCS[4])
        statFile.write("\n")
        statFile.write("- In-Degree Changes between first and latest revision -\n")
        statFile.write("min: %s\n" % compRCS[6])
        statFile.write("max: %s\n" % compRCS[7])
        statFile.write("mean: %s\n" % compRCS[8])
        statFile.write("median: %s\n" % compRCS[9])
        statFile.write("\n")
        statFile.write("- Out-Degree Changes between first and latest revision -\n")
        statFile.write("min: %s\n" % compRCS[11])
        statFile.write("max: %s\n" % compRCS[12])
        statFile.write("mean: %s\n" % compRCS[13])
        statFile.write("median: %s\n" % compRCS[14])
        statFile.write("\n")

        figure(figsize=(30,10))
        barInd = numpy.arange(len(compRCS[0]))
        barWidth = 0.8
        repBar = bar(barInd, compRCS[0], barWidth, color='r')
        #inBar  = bar(barInd+barWidth, compRCS[5], barWidth, color='y')
        #outBar = bar(barInd+barWidth*2, compRCS[10], barWidth, color='b')
        xlabel('Component')
        ylabel('Net Change')
        title('Component Revision Changes')
        grid(True)
        #legend((repBar[0], inBar[0], outBar[0]), ('Reputation', 'In-Degree', 'Out-Degree'))
        self._saveTFFig("comp_rev_changes.png")

        statFile.close()


    def output_user_types(self):
        userTypeFig1 = 'user_type_dist_designers.png'
        userTypeFig2 = 'user_type_dist_integrators.png'
        userTypeFig3 = 'user_type_dist_dualcontrib.png'
        userTypeStatFilename = 'user_type_stats.txt'

        # Cleanup the directory of previous output
        self._cleanup([userTypeFig1, userTypeFig2, userTypeFig2, userTypeStatFilename])

        statFile = open(self.outputDir + '/' + userTypeStatFilename, 'w')

        userTS = self.userTypeStats()
        statFile.write("-- User Type Statistics --\n")
        statFile.write("'Designer' User Count: " + str(len(userTS[0])) + "\n")
        statFile.write("'Integrator' User Count: " + str(len(userTS[1])) + "\n")
        statFile.write("'Dual-contributing' User Count: " + str(len(userTS[2])) + "\n")
        statFile.write("\n- Designer Users -\n")
        for user in userTS[3]:
            statFile.write(str(user))
            statFile.write("\n")
        statFile.write("\n- Dual-contributing Users -\n")
        for user in userTS[4]:
            statFile.write(str(user))
            statFile.write("\n")

        figure()
        hist(userTS[0], bins=20, range=(0,1))
        xlabel('Reputation')
        ylabel('Users')
        title('Designer User Reputation')
        grid(True)
        self._saveTFFig(userTypeFig1)

        figure()
        hist(userTS[1], bins=20, range=(0,1))
        xlabel('Reputation')
        ylabel('Users')
        title('Integrator User Reputation')
        grid(True)
        self._saveTFFig(userTypeFig2)

        figure()
        hist(userTS[2], bins=20, range=(0,1))
        xlabel('Reputation')
        ylabel('Users')
        title('Dual-Contributing User Reputation')
        grid(True)
        self._saveTFFig(userTypeFig3)

        statFile.close()


    #######################
    # Helper methods #
    #######################

    def _getUsers(self):
        self.logger.debug('Initiating storage connection...')
        trustmodel.init_model()
        return User.get_all(active_only=False)


    def _getComps(self):
        self.logger.debug('Initiating storage connection...')
        trustmodel.init_model()
        return Component.get_all()


    def _getCompsList(self):
        self.logger.debug('Initiating storage connection...')
        trustmodel.init_model()
        return ModelInterface().list_components(current_only=False)


    def _saveTFFig(self, filename, fileDir=None):
        if fileDir is None:
            fileDir = self.outputDir
        savefig(fileDir + "/" + filename)


    def _cleanup(self, files):
        if os.path.exists(self.outputDir):
            filetypes = ['png', 'csv', 'txt']
            for file in files:
                for filetype in filetypes:
                    path = self.outputDir + '/' + file + '.' + filetype
                    if os.path.exists(path):
                        os.remove(path)


    #############################
    # User-related stat methods #
    #############################

    def userRepStats(self):
        self.logger.info('Generating user reputation statistics...')
        repList = []
        repChangeList = []
        csvOut = []
        maxHist = 0
        for user in self._getUsers():
            repList.append(user.reputation)
            repHist = user.get_reputation_history()

            if len(repHist) > maxHist:
                maxHist = len(repHist)
            if len(repHist) > 0:
                repChangeList.append(repHist[-1].reputation - repHist[0].reputation)
            else:
                repChangeList.append(0)

            submitList = []
            if len(self.ucDict[user]) > 0:
                for comp in self.ucDict[user]:
                    if comp.submit:
                        submitList.append(comp)

            csvOut.append(dict(user = user.name, reputation = user.reputation,
                components = len(self.ucDict[user]),
                submitted = len(submitList)))

        return (maxHist, csvOut, sorted(repList), numpy.min(repList), numpy.max(repList),
                numpy.mean(repList), numpy.median(repList), numpy.var(repList),
                sorted(repChangeList), numpy.min(repChangeList), numpy.max(repChangeList),
                numpy.mean(repChangeList), numpy.median(repChangeList),
                numpy.var(repChangeList))


    def userCounts(self):
        self.logger.info('Generating user count statistics...')
        total = len(self.users)

        for comp in self._getComps():
            self.contribSet.update(comp.usernames)

        contributors = len(self.contribSet)

        return (total, contributors)


    def userComponentsRepStats(self, user):
        self.logger.info('Generating user-component reputation statistics...')
        repList = []
        submitList = []

        for comp in self.ucDict[user]:
            repList.append(comp.reputation)
            if comp.submit:
                submitList.append(comp)

        return (sorted(repList), numpy.min(repList), numpy.max(repList),
                numpy.mean(repList), numpy.median(repList), numpy.var(repList),
                float(len(submitList))/len(repList))


    def userRepContribStats(self):
        self.logger.info('Generating contributor user reputation statistics...')
        repListContrib = []
        repListNonContrib = []

        for user in self._getUsers():
            if user.name in self.contribSet:
                repListContrib.append(user.reputation)
            else:
                repListNonContrib.append(user.reputation)

        return (sorted(repListContrib), numpy.min(repListContrib), numpy.max(repListContrib),
                numpy.mean(repListContrib), numpy.median(repListContrib), numpy.var(repListContrib),
                sorted(repListNonContrib), numpy.min(repListNonContrib),
                numpy.max(repListNonContrib), numpy.mean(repListNonContrib),
                numpy.median(repListNonContrib), numpy.var(repListNonContrib))


    def userCompReps(self):
        self.logger.info('Generating component reputation statistics of the top 5% of users (by reputation)...')
        ucReps = []

        # Sort the user-component dictionary by the User reputation (sorted in descending order)
        uc = sorted(self.ucDict.items(), key=lambda item: item[0].reputation, reverse=True)

        # Find the ten percent count of total users
        perc = int(0.05 * len(self.ucDict.keys()))

        for i in range(perc):
            user = uc[i][0]

            # Sort the components by their first reputation history timestamps (approximation for creation time)
            # (sorted oldest to newest)
            sortedComps = sorted(uc[i][1], key=lambda comp: comp.reputation_history[-1], reverse=True)
            comps = []
            for comp in sortedComps:
                comps.append(comp.reputation)

            ucReps.append((user.name, user.reputation, comps))

        repList = zip(*ucReps)[1]

        print repList

        print "min : " + str(numpy.min(repList))
        print "max : " + str(numpy.max(repList))
        print "mean : " + str(numpy.mean(repList))
        print "median : " + str(numpy.median(repList))
        print "var : " + str(numpy.var(repList))

        return ucReps


    def userDesignsVsComponent(self):
        self.logger.info('Generating list of users top-level and regular component counts...')
        general = []
        topLevel = []

        for user in self._getUsers():
            # Get all of the components associated with this user
            comps = Component.get_by_author(user.name)
            compCount = len(comps)
            topLevelCount = 0

            # Determine how many of the user's components are top-level designs
            for comp in comps:
                if utilities.isTopLevelCompName(comp.name):
                    topLevelCount += 1

            general.append(compCount - topLevelCount)
            topLevel.append(topLevelCount)

        return (general, topLevel)


    def userTypeStats(self):
        self.logger.info('Generating user type statistics...')
        designerList = []
        designerRepList = []
        integratorList = []
        integratorRepList = []
        dualContribList = []
        dualContribRepList = []

        for user in self._getUsers():
            type = utilities.getUserContribType(user.name)

            if type[0] == 'designer':
                designerList.append(user)
                designerRepList.append(user.reputation)
            elif type[0] == 'integrator':
                integratorList.append(user)
                integratorRepList.append(user.reputation)

            # If the dual-contributor flag is True
            if type[1]:
                dualContribList.append(user)
                dualContribRepList.append(user.reputation)

        return (sorted(designerRepList), sorted(integratorRepList), sorted(dualContribRepList), designerList, dualContribList)


    ##################################
    # Component-related stat methods #
    ##################################

    def compRepStats(self):
        self.logger.info('Generating component reputation statistics...')
        repList = []
        inList = []
        outList = []
        csvOut = []
        maxHist = 0
        for comp in self._getComps():
            repList.append(comp.reputation)
            inList.append(self.in_degree[comp])
            outList.append(self.out_degree[comp])

            # Find max number of reputation iterations on components
            repHist = comp.get_reputation_history()

            if len(repHist) > maxHist:
                maxHist = len(repHist)

            csvOut.append(dict(component = comp.name + '_' + str(comp.revision),
                reputation = comp.reputation, tests = len(comp.get_tests()),
                in_degree = self.in_degree[comp],
                out_degree = self.out_degree[comp]))

        return (maxHist, csvOut, sorted(repList), numpy.min(repList), numpy.max(repList),
                numpy.mean(repList), numpy.median(repList), numpy.var(repList),
                scipy.stats.pearsonr(repList,inList),
                scipy.stats.pearsonr(repList,outList))


    def compTopLevelStats(self):
        self.logger.info('Generating top-level component statistics...')

        top = utilities.getTopLevelComps()

        top_byTestScore = sorted(top, key=lambda comp: utilities.getMaxTestScore(comp), reverse=True)
        top_byRep = sorted(top, key=lambda comp: comp.reputation, reverse=True)

        return (top_byTestScore, top_byRep)


    def compCounts(self):
        self.logger.info('Generating component count statistics...')
        submitList = []
        testList = []
        unsubmittedList = list(self._getComps())
        unusedList = []
        multirevsList = []

        for comp in self._getComps():
            # Build a list of submitted components
            if comp.submit:
                submitList.append(comp)
            # Build a list of unused components (if not submitted and no in-degree)
            elif comp.in_degree is 0:
                unusedList.append(comp)

            # Build a list of tested components
            if len(comp.tests) > 0:
                testList.append(comp)

            # Build a list of components with more than one revision
            if Component.get_revision_count(comp.name) > 1:
                multirevsList.append(comp)

        # Build a list of components not used in submissions
        for subm in submitList:
            unsubmittedList.remove(subm)
            for subc in subm.subcomponents:
                if subc in unsubmittedList:
                    unsubmittedList.remove(subc)

        # DEBUG - Print components that are in the tested list, but not in the submitted list
#       for comp in testList:
#           if not comp in submitList:
#               print comp

        total = len(self.comps)
        submitted = len(submitList)
        tested = len(testList)
        unsubmitted = len(unsubmittedList)
        unused = len(unusedList)
        multirevs = len(multirevsList)

        return (total, submitted, tested, self.in_degree, self.out_degree, unsubmitted, unused, multirevs)


    def compRevChangeStats(self):
        self.logger.info('Generating component revision change statistics...')
        repChangeList = []
        inChangeList = []
        outChangeList = []

        for comp in self._getCompsList():
            compRevCount = len(Component.get_by_name_all_revisions(comp))

            if compRevCount > 1:
                firstComp = Component.get_by_name(comp, revision=1)
                lastComp = Component.get_by_name(comp)

                repChangeList.append(lastComp.reputation - firstComp.reputation)
                inChangeList.append(self.in_degree[lastComp] - self.in_degree[firstComp])
                outChangeList.append(self.out_degree[lastComp] - self.out_degree[firstComp])

        return (sorted(repChangeList), numpy.min(repChangeList), numpy.max(repChangeList),
                numpy.mean(repChangeList), numpy.median(repChangeList),
                sorted(inChangeList), numpy.min(inChangeList), numpy.max(inChangeList),
                numpy.mean(inChangeList), numpy.median(inChangeList),
                sorted(outChangeList), numpy.min(outChangeList), numpy.max(outChangeList),
                numpy.mean(outChangeList), numpy.median(outChangeList))


    def compRepSubmittedStats(self):
        self.logger.info('Generating component reputation submitted statistics...')
        repListSubmit = []
        repListNonSubmit = []

        for comp in self._getComps():
            if comp.submit:
                repListSubmit.append(comp.reputation)
            else:
                repListNonSubmit.append(comp.reputation)

        return (sorted(repListSubmit), numpy.min(repListSubmit), numpy.max(repListSubmit),
                numpy.mean(repListSubmit), numpy.median(repListSubmit), numpy.var(repListSubmit),
                sorted(repListNonSubmit), numpy.min(repListNonSubmit),
                numpy.max(repListNonSubmit), numpy.mean(repListNonSubmit),
                numpy.median(repListNonSubmit), numpy.var(repListNonSubmit))


#--------------------------------------------------------------------------------

# Test suite

class TestStats(unittest.TestCase):
    def setUp(self):
        self.dump = 'dump-2013-31-1'
        utilities.loadDatadump(self.dump)

        self.users = getUsers()
        self.comps = getComps()

        unpickledDatadump = utilities.unpickleDatadumpContents(self.dump)
        self.users_pkl = unpickledDatadump[0]
        self.comps_pkl = unpickledDatadump[1]


    def test_userRepStats(self):
        output = userRepStats(self.users)

        self.assertEqual(output[0], 0)
        self.assertEqual(output[1], 1)
        self.assertEqual(output[2], 1)
        self.assertEqual(output[3], 1)
        self.assertEqual(output[4], 1)


    def test_userCounts(self):
        output = userCounts(self.users)

        self.assertEqual(output[0], 100)
        self.assertEqual(output[1], 10)


    def tearDown(self):
        close_all_mongo_connections()

#--------------------------------------------------------------------------------

# Module testing

if __name__ == "__main__":
    unittest.main()
