'''
Reference:
Antikacioglu, Arda, and R. Ravi.
"Post processing recommender systems for diversity."
In Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 707-716. 2017.
'''

import subprocess, glob, math, sys, os
from itertools import *
from scipy.stats import entropy
from math import ceil, log
from random import *
from time import time

import numpy as np
from numpy.random import choice

import argparse
from librec_auto.core import read_config_file
from pathlib import Path
import re
from librec_auto.core.util.xml_utils import single_xpath
import multiprocessing
from librec_auto.core.cmd.rerank import Rerank_Helper, User_Helper, Reranker
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class SuperGraph:
    def __init__(self, table, l, r, m):
        self.table, self.l, self.r, self.m = table, l, r, m
        self.cdist = {}
        self.adist = {}

    def filter(self, threshold=0, top_k=None):
        '''filters the supergraph to include the either the top k recommendations or the
           recommendations which have relevance above threshold'''
        new_table = {}
        m = 0
        if top_k is not None:
            for u in range(1, self.l + 1):
                new_table[u] = self.table[u][:top_k]
                m += top_k
        else:
            for u in range(1, self.l + 1):
                new_table[u] = self.table[u][:10]
                v = 11
                while v < len(self.table[u]) and self.table[u][v][1] >= threshold:
                    new_table[u].append(self.table[u][v])
                    v += 1
                m += v - 1
        return SuperGraph(new_table, self.l, self.r, m)

    def printOut(self, fn_out):
        fn_out = open(fn_out, 'w')
        for u in range(1, self.l + 1):
            print >> fn_out, '\n'.join('%d\t%d\t%.4f' % (u, v, rating) for v, rating in self.table[u])

    def uniformC(self, c):
        '''produces the uniform display constraints'''
        if c not in self.cdist:
            self.cdist[c] = [0] + [c] * self.l
        return self.cdist[c]

    def uniformA(self, c):
        '''produces the uniform target degree distribution'''
        aa = 1.0 * c * self.l / self.r
        A = [0] + [aa] * (self.r)
        return A

    def proportionalA(self, c):
        '''produces the degree distribution that is proportional to the supergraph's distribution'''
        A = [0] * (self.r + 1)
        for u in range(1, self.l + 1):
            for v, rating in self.table[u]:
                A[v] += 1

        sumA = sum(A)
        for v in range(1, self.r + 1):
            A[v] *= (1.0 * (c * self.l)) / sumA
        return A

    def proportionalAtoTop(self, c):
        '''produces a target distribution that is proportional to the top c recommendations'''
        A = [0] * (self.r + 1)
        for u in range(1, self.l + 1):
            for v, rating in islice(self.table[u], 0, c):
                A[v] += 1

        sumA = sum(A)
        for v in range(1, self.r + 1):
            A[v] *= (1.0 * (c * self.l)) / sumA
        return A

    def allOnesA(self):
        '''produces the aggregate diversity target distribution'''
        A = [1] * (self.r + 1)
        A[0] = 0
        return A

    def convexCombinationA(self, c, alpha=0):
        '''produces a blend of the uniform and proportional target distributions'''
        if (c, alpha) not in self.adist:
            A1 = self.proportionalA(c)
            A2 = self.uniformA(c)
            A3 = [a1 * alpha + a2 * (1 - alpha) for a1, a2 in zip(A1, A2)]
            self.adist[c, alpha] = self.roundDistribution(A=A3, target=self.l * c)

        return self.adist[c, alpha]

    def convexCombinationAtoTop(self, c, alpha=0):
        '''produces a blend of the uniform and proportional target distributions'''
        if (c, alpha) not in self.adist:
            A1 = self.proportionalAtoTop(c)
            A2 = self.uniformA(c)
            A3 = [a1 * alpha + a2 * (1 - alpha) for a1, a2 in zip(A1, A2)]
            self.adist[c, alpha] = self.roundDistribution(A=A3, target=self.l * c)
        return self.adist[c, alpha]

    def roundDistribution(self, A, target):
        '''round the degree distribution to integers'''

        def findCap(A, target, lo=0, hi=1000):
            if hi == lo + 1: return hi
            cap = (lo + hi) / 2
            newsum = sum(min(A[v], cap) for v in range(1, self.r + 1))
            if newsum <= target:
                return findCap(A, target, cap, hi)
            else:
                return findCap(A, target, lo, cap)

        for v in range(1, self.r + 1):
            A[v] = max(1, int(math.ceil(A[v])))

        total = sum(A)
        v = 1
        while 1:
            if v == self.r: v = 1
            if total == target: break
            if A[v] > 1:
                total -= 1
                A[v] -= 1
            v += 1

        return A

    def export(self):
        return self.table, self.l, self.r, self.m

    @staticmethod
    def readRecommendationTable(fn_in, user_original_to_new, item_original_to_new):
        '''reads a list of candidate recommendations from fn_in. assumes one recommendation per line
           and that recommendations are space separated triples of the form (user, item, rating)'''
        f_in = open(fn_in)
        table = {}
        l = r = 0

        for line in f_in:
            u, i, rating = line.split(',')
            u, i, rating = int(u), int(i), float(rating)
            u_new = user_original_to_new[u]
            i_new = item_original_to_new[i]
            l = max(u_new, l)
            r = max(i_new, r)
            if u_new in table:
                table[u_new].append((i_new, rating))
            else:
                table[u_new] = [(i_new, rating)]

        for u in range(1, l + 1):
            if u not in table: table[u] = []
            deficit = 10 - len(table[u])
            for _ in range(deficit):
                table[u].append((randint(1, r), 2.5))

        m = sum(len(table[u]) for u in range(1, l + 1))
        for u, v in table.items():
            v.sort(key=lambda x: -x[1])

        return SuperGraph(table, l, r, m)

class Solver:
    def __init__(self, superg):
        self.superg = superg

    def writeDMXProblem(self, C, A, lambd, mu, fn_out, stages=1, stage_amount=5):
        '''writes out the dmx problem for the bicriteria discrepancy reduction problem with
           C            as the display constraints
           A            as the target degree distribution
           lambd        as the relative weight of the discrepancy term
           mu           as the relative weight of the relevance term
           test_fn      as the a list of held out ratings which are known to be relevant
           stages       as the number of slopes of the degree overrun penalty
           stage_amount as the length of each leg of the slopes
           fn_out       as the name of the output file'''

        INFINITY = 2 * sum(C)
        f_out = open(fn_out, 'w')
        table, l, r, m = self.superg.export()

        # sanity checks
        assert A[0] == C[0] == 0
        assert all(len(table[u]) >= C[u] for u in range(1, l + 1))
        assert len(C) == l + 1
        assert len(A) == r + 1
        assert sum(A) <= sum(C)

        # print 'c Problem line (nodes, links)'
        f_out.write('p min %d %d \n' % (l + r + stages + 1, m + (stages + 1) * r + stages))

        # print 'c Node descriptor lines (supply+ or demand-)'
        for i in range(1, l + 1):
            f_out.write('n %d %d \n' % (i, C[i]))
        f_out.write('n %d %d \n' % (l + r + 2, -sum(C)))

        # print 'c Arc descriptor lines (from, to, minflow, maxflow, cost)'
        for u in range(1, l + 1):
            for v, rating in table[u]:
                f_out.write('a %d %d %d %d %.2f \n' % (u, l + v, 0, 1, -rating * mu))

        for v in range(1, r + 1):
            f_out.write('a %d %d %d %d %d \n' % (l + v, l + r + 1, 0, A[v], 0))
            for stage in range(1, stages):
                f_out.write('a %d %d %d %d %d \n' % (l + v, l + r + stage + 1, 0, stage_amount, 2 * stage * lambd))
            f_out.write('a %d %d %d %d %d \n' % (l + v, l + r + stages + 1, 0, INFINITY, 2 * stages * lambd))

        for stage in range(1, stages + 1):
            f_out.write('a %d %d %d %d %d \n' % (l + r + stage, l + r + stage + 1, 0, INFINITY, 0))

    def writeDMXProblemGoal(self, C, A, lambd, mu, fn_out, goal=None, stages=1, stage_amount=5):
        '''writes out the dmx problem for the goal programming discrepancy reduction problem with
           C            as the display constraints
           A            as the target degree distribution
           lambd        as the relative weight of the discrepancy term
           mu           as the relative weight of the relevance term
           test_fn      as the a list of held out ratings which are known to be relevant
           stages       as the number of slopes of the degree overrun penalty
           stage_amount as the length of each leg of the slopes
           fn_out       as the name of the output file'''
        INFINITY = 2 * sum(C)
        f_out = open(fn_out, 'w')
        table, l, r, m = self.superg.export()

        # sanity checks
        assert A[0] == C[0] == 0
        assert len(C) == l + 1
        assert len(A) == r + 1
        assert sum(A) <= sum(C)

        # print 'c Problem line (nodes, links)'
        print(f_out, 'p min %d %d' % (l + r + stages + 1, m + (stages + 1) * r + stages))

        # print 'c Node descriptor lines (supply+ or demand-)'
        for i in range(1, l + 1):
            print(f_out, 'n %d %d' % (i, C[i]))
        print(f_out, 'n %d %d' % (l + r + 2, -sum(C)))

        # print 'c Arc descriptor lines (from, to, minflow, maxflow, cost)'
        for u in range(1, l + 1):
            for v, rating in table[u]:
                print(f_out, 'a %d %d %d %d %.5f' % (u, l + v, 0, 1, -rating))

        for v in range(1, r + 1):
            print(f_out, 'a %d %d %d %d %d' % (l + v, l + r + 1, 0, A[v], 0))
            print(f_out, 'a %d %d %d %d %d' % (l + v, l + r + 2, 0, INFINITY, 0))

        for stage in range(1, stages + 1):
            print(f_out, 'a %d %d %d %d %d' % (l + r + stage, l + r + stage + 1, goal, INFINITY, 0))

    def writeDMXProblemCategory(self, C, A, lambd, mu, fn_out, categories, categoryTargets):
        '''category is a dictionary mapping vertices to their category id [1..k]'''
        '''category targets is a list denoting the target for each category'''
        if not goal: goal = sum(C)
        INFINITY = sum(C)
        f_out = open(fn_out, 'w')
        table, l, r, m = self.superg.export()

        num_categories = len(categories)
        collector = l + r + 3 * num_categories + 1
        supersink = l + r + 3 * num_categories + 2
        assert A[0] == C[0] == 0
        assert len(C) == l + 1
        assert len(A) == r + 1
        assert sum(A) <= sum(C)

        # print 'c Problem line (nodes, links)'
        print(f_out, 'p min %d %d' % (l + r + 3 * num_categories + 2, m + 2 * r + 4 * num_categories + 2))

        # print 'c Node descriptor lines (supply+ or demand-)'
        for i in range(1, l + 1):
            print(f_out, 'n %d %d' % (i, C[i]))
        for category in range(1, num_categories + 1):
            print(f_out, 'n %d %d' % (l + r + 3 * category + 2, categoryTargets[category]))
        print(f_out, 'n %d %d' % (supersink, l * c - sum(categoryTargets)))

        # print 'c Arc descriptor lines (from, to, minflow, maxflow, cost)'
        for u in range(1, l + 1):
            for v, rating in table[u]:
                print(f_out, 'a %d %d %d %d %.2f' % (u, l + v, 0, 1, rating))

        for v in range(1, r + 1):
            print(f_out, 'a %d %d %d %d %d' % (l + v, l + r + 3 * category[v], 0, INFINITY, 0))
            print(f_out, 'a %d %d %d %d %d' % (l + v, l + r + 3 * category[v] + 1, 0, INFINITY, 1))

        for category in range(1, num_categories + 1):
            print(f_out, 'a %d %d %d %d %d' % (
            l + r + 3 * category + 1, l + r + 3 * category + 2, categoryTargets[category], 0))
            print(f_out, 'a %d %d %d %d %d' % (l + r + 3 * category + 1, collector, INFINITY, 0))
            print(f_out, 'a %d %d %d %d %d' % (collector, l + r + 3 * category + 2, INFINITY, 1))
            print(f_out, 'a %d %d %d %d %d' % (l + r + 3 * category + 2, supersink, INFINITY, 0))

        print(f_out, 'a %d %d %d %d %d' % (collector, supersink, 0, INFINITY, 0))

    def degree_distribution(self, edges):
        '''calculates the degree distribution of the edge list edges'''
        table, l, r, m = self.superg.export()
        AA = [0] * (r + 1)
        for u, v in edges:
            AA[v - l] += 1
        return np.array(AA)

    def entropy(self, arr):
        '''calculates the entropy of the normalized degree distribution'''
        return entropy(arr)

    def gini(self, array):
        '''calculates the gini index of the degree distribution'''
        sorted_list = sorted(array)
        height, area = 0, 0
        for value in sorted_list:
            height += value
            area += height - value / 2.
        fair_area = height * len(array) / 2.
        return (fair_area - area) / fair_area

    def readOutput(self, dmx_fn):
        '''calls MCFSolve to solve the dmx problem and reads the set of edges'''
        start = time()
        cmd = ['./MyMCFSolve', dmx_fn]
        g1 = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].split('\n')
        duration = time() - start
        g2 = [g1[x].split() for x in range(2, len(g1) - 2) if g1[x]]
        g3 = {(int(u), int(i)) for u, i in g2 if
              u.isdigit() and i.isdigit() and int(i) <= self.superg.l + self.superg.r}
        return g3, duration

    def solutionMetrics(self, C, A, edges, test_fn):
        '''calculates the aggregate diversity, precision and discrepancy of the solutions described by edges'''
        table, l, r, m = self.superg.export()
        ratings = 0.0
        AA = [0] * (r + 1)

        tests = set()
        for line in open(test_fn):
            u, v = map(int, line.split()[:2])
            tests.add((u, v + l))

        for u, v in edges:
            AA[v - l] += 1

        ctr = 0
        for u in range(1, l + 1):
            for v, rating in table[u]:
                if (u, l + v) in edges:
                    ratings += rating

        PRECISION = len(tests & edges) * 1. / (len(set(u for u, v in tests)) * C[1])
        AGGDIV = sum(a > 0 for a in AA) * 1. / r
        return sum(abs(A[i] - AA[i]) for i in range(1, r + 1)), ratings / sum(C), AGGDIV, PRECISION

    def lowerBound(self, A):
        '''calculates the trivial lower bound on discrepancy given the edges of the supergraph'''
        table, l, r, m = self.superg.export()
        AA = [0] * (r + 1)
        for u in table:
            for v, rating in table[u]:
                AA[v] += 1
        return 2 * sum(max(0, A[i] - AA[i]) for i in range(1, r + 1))

    def solveGreedy(self, C, A, test_fn):
        '''implements the greedy algorithm'''
        start = time()
        table, l, r, m = self.superg.export()
        edges = set()
        deg_dist = np.zeros(r + 10)
        AA = self.superg.proportionalA(C[1])

        order = range(1, l + 1)
        shuffle(order)
        for u in order:
            discrepancy_reducers = [v for v, rating in table[u] if deg_dist[v] < A[v]]
            d_weights = [rating for v, rating in table[u] if deg_dist[v] < A[v]]
            sum_d_weights = sum(d_weights)
            d_weights = [rating * 1. / sum_d_weights for rating in d_weights]

            rest = [v for v, rating in table[u] if deg_dist[v] >= A[v]]
            r_weights = [rating for v, rating in table[u] if deg_dist[v] >= A[v]]
            sum_r_weights = sum(r_weights)
            r_weights = [rating * 1. / sum_r_weights for rating in r_weights]

            neighbors = []
            if len(discrepancy_reducers) >= C[u]:
                neighbors = list(choice(discrepancy_reducers, replace=False, size=C[u], p=d_weights))
            else:
                left_over = C[u] - len(discrepancy_reducers)
                neighbors = discrepancy_reducers
                neighbors += list(choice(rest, replace=False, size=left_over, p=r_weights))

            for v in neighbors:
                edges.add((u, v + l))
                deg_dist[v] += 1

        duration = time() - start
        GINI = self.gini(deg_dist)
        ENT = self.entropy(deg_dist / (1. * sum(C)))
        SOLD, SOLR, SOLA, P = self.solutionMetrics(C, A, edges, test_fn)
        return (SOLD / 2. / sum(C), SOLR, SOLA, P, GINI, ENT, deg_dist, duration)

    def solveExternal(self, C, A, train_in, rec_in, test_fn, script_name="FD"):
        '''calls an external script to diversify recommendations'''
        '''the external script must take as input a single file of candidate recommendations'''
        '''the cmd variable below must be changed to the path of the external solver'''

        rec_in = rec_in[:-4]
        dummy_rec_in = rec_in + '_.txt'
        self.superg.printOut(dummy_rec_in)

        start = time()

        cmd = "CHANGE THIS TO THE PATH OF THE SCRIPT YOU WOULD LIKE TO USE"
        cmd = ' '.join([cmd, train_in, rec_in + '_', script_name])

        subprocess.call(cmd, shell=True)
        duration = time() - start
        fn_in = '%s__%s.txt' % (rec_in, script_name)

        table, l, r, m = self.superg.export()

        user_deg = [0] * (l + 1)
        deg_dist = np.zeros(r + 1)
        edges = set()
        for line in open(fn_in):
            u, v, _ = line.strip().split()
            u = int(u)
            v = int(v)
            if user_deg[u] < C[u]:
                edges.add((u, v + l))
                user_deg[u] += 1
                deg_dist[v] += 1

        GINI = self.gini(deg_dist)
        ENT = self.entropy(deg_dist / (1. * sum(C)))
        SOLD, SOLR, SOLA, P = self.solutionMetrics(C, A, edges, test_fn)
        return (SOLD / 2. / sum(C), SOLR, SOLA, P, GINI, ENT, deg_dist, duration)

    def solveStandard(self, C, A, test_fn):
        table, l, r, m = self.superg.export()

        edges = set()
        for u in range(1, l + 1):
            for i in range(C[u]):
                edges.add((u, l + table[u][i][0]))

        SOLD, SOLR, SOLA, P = self.solutionMetrics(C, A, edges, test_fn)
        deg_dist = self.degree_distribution(edges)
        GINI = self.gini(deg_dist)
        ENT = self.entropy(deg_dist / (1. * sum(C)))
        return (SOLD / 2. / sum(C), SOLR, SOLA, P, GINI, ENT, deg_dist, 0)

    def solve(self, C, A, dmx_fn, test_fn, lambd=1, mu=0, stages=1, stage_amount=5):
        '''solves the recommendation problem encoded by dmx_fn using the bicriteria method
           C            as the display constraints
           A            as the target degree distribution
           lambd        as the relative weight of the discrepancy term
           mu           as the relative weight of the relevance term
           test_fn      as the a list of held out ratings which are known to be relevant
           stages       as the number of slopes of the degree overrun penalty
           stage_amount as the length of each leg of the slopes
           fn_out       as the name of the output file'''

        l, r = self.superg.l, self.superg.r
        self.writeDMXProblem(C, A, lambd, mu, dmx_fn, stages, stage_amount)
        # edges, duration = self.readOutput(dmx_fn)
        # deg_dist = self.degree_distribution(edges)
        # LOWERBOUND = self.lowerBound(A)
        # SOLD, SOLR, SOLA, P = self.solutionMetrics(C, A, edges, test_fn)
        # GINI = self.gini(deg_dist)
        # ENT = self.entropy(deg_dist / (1. * sum(C)))
        # return (SOLD / 2. / sum(C), SOLR, SOLA, P, GINI, ENT, deg_dist, duration)

    def solveWithGoal(self, C, A, dmx_fn, test_fn, lambd=1, mu=0, stages=1, stage_amount=5):
        '''solves the recommendation problem encoded by dmx_fn using the goal programming method
           C            as the display constraints
           A            as the target degree distribution
           lambd        as the relative weight of the discrepancy term
           mu           as the relative weight of the relevance term
           test_fn      as the a list of held out ratings which are known to be relevant
           stages       as the number of slopes of the degree overrun penalty
           stage_amount as the length of each leg of the slopes
           fn_out       as the name of the output file'''

        l, r = self.superg.l, self.superg.r
        self.writeDMXProblem(C, A, 1, 0, dmx_fn, stages, stage_amount)
        edges, duration1 = self.readOutput(dmx_fn)
        LOWERBOUND = self.lowerBound(A)
        SOLD, SOLR, SOLA, P = self.solutionMetrics(C, A, edges, test_fn)
        OLDSOLD = int(SOLD * 2 * sum(C) + 1)

        self.writeDMXProblemGoal(C, A, 0, 1, dmx_fn, sum(C) - SOLD / 2 - 1, stages, stage_amount)
        edges, duration2 = self.readOutput(dmx_fn)
        deg_dist = self.degree_distribution(edges)
        SOLD, SOLR, SOLA, P = self.solutionMetrics(C, A, edges, test_fn)
        GINI = self.gini(deg_dist)
        ENT = self.entropy(deg_dist / (1. * sum(C)))

        return (SOLD / 2. / sum(C), SOLR, SOLA, P, GINI, ENT, deg_dist, duration1 + duration2)


class DMHelper():
    target_dist = 0.0
    mu = 0.0
    dist_shape = ''
    max_len = 0

def set_helper(target_dist, max_len, mu, dist_shape):
    helper = DMHelper()
    helper.target_dist = target_dist
    helper.mu = mu
    helper.max_len = max_len
    helper.dist_shape = dist_shape
    return helper

RESULT_FILE_PATTERN = 'out-(\d+).txt'
INPUT_FILE_PATTERN = 'cv_\d+'

def read_args():
    """
    Parse command line arguments.
    :return:
    """
    parser = argparse.ArgumentParser(description='Generic re-ranking script')
    parser.add_argument('conf', help='Name of configuration file')
    parser.add_argument('original', help='Path to original results directory')
    parser.add_argument('result', help='Path to destination results directory')
    parser.add_argument('--max_len', help='The maximum number of items to return in each list', default=10)
    parser.add_argument('--target_dist', help='Weight of target distribution.', default=1)
    parser.add_argument('--dist_shape', help='Shape of target distribution', default='uniform')
    parser.add_argument('--mu', help='Importance weight of relevance', default="0.01")
    parser.add_argument('--method', help='reranking method')

    input_args = parser.parse_args()
    return vars(input_args)

def enumerate_results(result_path):
    pat = re.compile(RESULT_FILE_PATTERN)
    files = [file for file in result_path.iterdir() if pat.match(file.name)]
    files.sort()
    return files

def map_user_item_id(file_path):
    user_original_to_new, user_new_to_original, item_original_to_new, item_new_to_original = {}, {}, {}, {}
    long_rec = pd.read_csv(file_path, names=['userid', 'itemid', 'rating'])
    users = list(long_rec.userid.unique())
    items = list(long_rec.itemid.unique())
    for i in range(len(users)):
        user_original_to_new[users[i]] = i+1
        user_new_to_original[i+1] = users[i]
    for i in range(len(items)):
        item_original_to_new[items[i]] = i+1
        item_new_to_original[i+1] = items[i]
    return user_original_to_new, user_new_to_original, item_original_to_new, item_new_to_original

def generate_dm(helper, original_results_path, file_path, user_original_to_new, item_original_to_new):
    sg = SuperGraph.readRecommendationTable(file_path, user_original_to_new, item_original_to_new)
    c = sg.uniformC(helper.max_len)
    # a_constraint = 1
    # mu = 0.01
    solver = Solver(sg)
    a = sg.uniformA(helper.target_dist)#[0] + [1] * sg.r
    solver.solve(c, a, str(original_results_path)+"/temp.dmx", "", 1, helper.mu, 1, 5)
    f = open(str(original_results_path)+"/temp", "w")
    # cmd = ("/Users/m.mansouryuva.nl/Research/Librec-Auto/github-master/librec-auto/librec_auto/MCFSolve", str(original_results_path)+"/temp" + ".dmx", ">", str(original_results_path)+"/temp")
    cmd = (os.path.dirname(os.path.realpath(__file__))+"/MCFSolve", str(original_results_path)+"/temp" + ".dmx", ">", str(original_results_path)+"/temp")
    g1 = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT)
    # g1 = subprocess.call("./MCFSolve " + str(original_results_path)+"/temp" + ".dmx > " + str(original_results_path)+"/temp", stdout=f)
    return sg

def output_reranked(sg, source_path, dest_results_path, file_path, user_new_to_original, item_new_to_original):
    with open(source_path, 'r') as file:
        data = file.read()
    g1 = data.split('\n')
    g2 = [g1[x].split() for x in range(2, len(g1) - 2) if g1[x]]
    g3 = {(int(u), int(i)) for u, i in g2 if u.isdigit() and i.isdigit() and int(i) <= sg.l + sg.r and int(u) <= sg.l}
    f = open(dest_results_path / file_path.name, "w")
    for u, v in g3:
        f.write(str(user_new_to_original[u]) + "," + str(item_new_to_original[v-sg.l]) + "," + str(0) + "\n")
    f.close()

def main():
    args = read_args()
    # config = read_config_file(args['conf'], '.')

    original_results_path = Path(args['original'])
    result_files = enumerate_results(original_results_path)

    dest_results_path = Path(args['result'])

    target_dist = float(args['target_dist'])
    mu = float(args['mu'])
    max_len = int(args['max_len'])
    dist_shape = args['dist_shape'] = args['dist_shape']

    helper = set_helper(target_dist, max_len, mu, dist_shape)

    for file_path in result_files:
        user_original_to_new, user_new_to_original, item_original_to_new, item_new_to_original = map_user_item_id(file_path)
        sg = generate_dm(helper, original_results_path,file_path, user_original_to_new, item_original_to_new)
        output_reranked(sg, str(original_results_path)+"/temp", dest_results_path, file_path, user_new_to_original, item_new_to_original)
    return 0

if __name__ == '__main__':
    main()