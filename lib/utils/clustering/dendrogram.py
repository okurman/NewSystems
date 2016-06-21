__author__ = 'hudaiber'

import os
import sys
if sys.platform == 'darwin':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))
elif sys.platform == 'linux2':
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/lib/BioPy/'))
    sys.path.append(os.path.join(os.path.expanduser('~'),'Projects/SystemFiles/'))

import global_variables as gv

import numpy as np
import scipy.spatial.distance as ssd
from scipy.cluster.hierarchy import dendrogram, linkage, to_tree, leaves_list
import matplotlib.pyplot as plt

from lib.utils import tools as t
gnm2weight = t.map_genome2weight()

# file2org = {l.split()[0]:l.strip().split()[1] for l in open(os.path.join(gv.project_data_path,'cas1402/file2org.txt')).readlines()}
# file2crispr_type = {l.split('\t')[0]:l.strip().split('\t')[1].split(';') for l in open(os.path.join(gv.project_data_path,'cas1402/file2type.tab'))}



def fancy_dendrogram(*args, **kwargs):

    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    title = kwargs.pop('title', 0)
    xlabel = kwargs.pop('xlabel', 0)
    ylabel = kwargs.pop('ylabel', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata


def plot_dendrogram(Z, dendogram_file_name):

    root = to_tree(Z)
    threshold = root.dist / 3.0
    all_leaves = get_leaves(root)

    plt.figure(figsize=(30, 30))
    title = 'Hierarchical Clustering Dendrogram( %d leaves)' % len(all_leaves)
    xlabel = 'loci'
    ylabel = 'distance'

    fancy_dendrogram(
        Z,
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=4.,  # font size for the x axis labels
        annotate_above=10,
        max_d=threshold,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel
    )

    # plt.savefig(os.path.join(report_path, 'dendrogram_distance_array.eps'), format='eps', dpi=900)
    if dendogram_file_name.endswith('pdf'):
        plt.savefig(dendogram_file_name, format='pdf')
    elif dendogram_file_name.endswith('png'):
        plt.savefig(dendogram_file_name, format='png')
    else:
        raise NotImplemented('File format has to be either png or pdf')

    plt.close()
    return threshold


def plot_dendrogram_from_score_matrix(M, dendogram_file_name, inf_default=50):

    if not (M == np.transpose(M)).all():

        M += np.transpose(M)
        M = np.negative(np.log(M))
        np.fill_diagonal(M, 0)
        inf_idx = np.isinf(M)
        M[inf_idx] = inf_default

    M_array = ssd.squareform(M)
    Z = linkage(M_array, method='average')

    return plot_dendrogram(Z, dendogram_file_name)


def get_leaves(root_node):

    if root_node.is_leaf():
        return [root_node.id]
    else:
        return get_leaves(root_node.left) + get_leaves(root_node.right)


class Node(object):

    def __init__(self, other, parent=None):
        self.count = other.count
        self.dist = other.dist
        self.id = other.id
        self.is_leaf = other.is_leaf
        self.parent = parent
        self.left = None
        self.right = None


def clone_graph(root_node, parent=None):
    new_node = Node(root_node, parent)
    if new_node.is_leaf():
        return new_node
    else:
        new_node.left  = clone_graph(root_node.left,  new_node)
        new_node.right = clone_graph(root_node.right, new_node)
        return new_node


def get_leaves(root_node):

    if root_node.is_leaf():
        return [root_node.id]
    else:
        return get_leaves(root_node.left) + get_leaves(root_node.right)


def get_nodes(root_node):

    if root_node.is_leaf():
        return [root_node]
    else:
        return get_nodes(root_node.left) + [root_node] + get_nodes(root_node.right)


def break_down(root_node, size_limit=1000):

    if root_node.count < size_limit:
        return [root_node]
    else:
        return break_down(root_node.left, size_limit) + break_down(root_node.right, size_limit)



def classify_by_scores(M, threshold, loci, return_file_names=None):

    M_array = ssd.squareform(M)

    Z = linkage(M_array, method='average')

    root = to_tree(Z)
    root = clone_graph(root)

    nodes = get_nodes(root)
    id2node = {node.id: node for node in nodes}

    leaf_ids = leaves_list(Z)

    cnt = 0
    i = 0
    total_count = 1

    pool = []

    while True:
        cur_node = id2node[leaf_ids[i]]
        parent_dist = cur_node.parent.dist

        while parent_dist < threshold:
            cur_node = cur_node.parent
            parent_dist = cur_node.parent.dist

        cur_leaf_ids = get_leaves(cur_node)

        pool.append([id for id in cur_leaf_ids])

        total_count += cur_node.count

        i += len(cur_leaf_ids)

        if i >= len(leaf_ids)-1:
            break
        cnt += 1

    clusters = [l for l in pool if len(l) > 1]
    singles = [l[0] for l in pool if len(l) == 1]

    clusters = sorted(clusters, key=lambda x: len(x), reverse=True)

    if return_file_names:

        clusters_fn = []

        for cluster in clusters:

            clusters_fn.append([os.path.basename(loci[i].file_name) for i in cluster])

        singles_fn = [ os.path.basename(loci[i].file_name) for i in singles]

        return singles_fn, clusters_fn

    else:

        return singles, clusters


def classify_by_scores_cas1402(M, threshold, loci):

    M_array = ssd.squareform(M)

    Z = linkage(M_array, method='average')

    root = to_tree(Z)
    root = clone_graph(root)

    nodes = get_nodes(root)
    id2node = {node.id: node for node in nodes}

    leaf_ids = leaves_list(Z)

    cnt = 0
    i = 0
    total_count = 1

    pool = []

    while True:
        cur_node = id2node[leaf_ids[i]]
        parent_dist = cur_node.parent.dist

        while parent_dist < threshold:
            cur_node = cur_node.parent
            parent_dist = cur_node.parent.dist

        cur_leaf_ids = get_leaves(cur_node)

        pool.append([id for id in cur_leaf_ids])

        total_count += cur_node.count

        i += len(cur_leaf_ids)

        if i >= len(leaf_ids)-1:
            break
        cnt += 1

    to_collapse = [l for l in pool if len(l) > 1]
    singles = [l[0] for l in pool if len(l) == 1]

    to_collapse = sorted(to_collapse, key=lambda x: len(x), reverse=True)

    sum_errors = []
    entropies = []
    weights = []
    to_collapse_retval = []

    cluster_ind = 0

    for cluster in to_collapse:

        cluster_ind += 1
        type2cnt = {}
        type2wgt = {}

        cluster_files = [loci[id].file_name.split('/')[-1] for id in cluster]

        cluster_weight = 0

        for _f in cluster_files:

            file_weight = gnm2weight[file2org[_f]]
            cluster_weight += file_weight

            if _f not in file2crispr_type:
                t.update_dictionary(type2cnt, "NA", 1)
                t.update_dictionary(type2wgt, "NA", file_weight)
                continue
            for _type in file2crispr_type[_f]:
                t.update_dictionary(type2cnt, _type, 1)
                t.update_dictionary(type2wgt, _type, file_weight)

        _weights = np.array(type2wgt.values(), dtype=np.float)

        sum_errors.append(np.sum(np.square(_weights - np.mean(_weights))))

        _weights /= np.sum(_weights)
        entropy = -1 * np.sum(_weights * np.log(_weights))
        entropies.append(entropy)
        weights.append(cluster_weight)

        to_collapse_retval.append((cluster, type2cnt, type2wgt, entropy))

    sum_errors = np.average(sum_errors)

    entropies = np.array(entropies)
    weights = np.array(weights)

    average_entropy = np.sum(entropies * weights) / np.sum(weights)
    sum_errors = np.sum(sum_errors * weights) / np.sum(weights)

    return singles, to_collapse_retval, sum_errors, average_entropy


def classify_by_scores_cas4(M, threshold, loci, inf_default=50):

    if not (M == np.transpose(M)).all():

        M += np.transpose(M)
        M = np.negative(np.log(M))
        np.fill_diagonal(M, 0)
        inf_idx = np.isinf(M)
        M[inf_idx] = inf_default

    M_array = ssd.squareform(M)

    Z = linkage(M_array, method='average')

    root = to_tree(Z)
    root = clone_graph(root)

    nodes = get_nodes(root)
    id2node = {node.id: node for node in nodes}

    leaf_ids = leaves_list(Z)

    cnt = 0
    i = 0
    total_count = 1

    pool = []

    while True:
        cur_node = id2node[leaf_ids[i]]
        parent_dist = cur_node.parent.dist

        while parent_dist < threshold:
            cur_node = cur_node.parent
            parent_dist = cur_node.parent.dist

        cur_leaf_ids = get_leaves(cur_node)

        pool.append([id for id in cur_leaf_ids])

        total_count += cur_node.count

        i += len(cur_leaf_ids)

        if i >= len(leaf_ids)-1:
            break
        cnt += 1

    to_collapse = [l for l in pool if len(l) > 1]
    singles = [l[0] for l in pool if len(l) == 1]

    to_collapse = sorted(to_collapse, key=lambda x: len(x), reverse=True)

    entropies = []
    to_collapse_retval = []

    cluster_ind = 0

    for cluster in to_collapse:

        cluster_ind += 1
        type2cnt = {}

        for pos in cluster:
            t.update_dictionary(type2cnt, loci[pos].crispr_type, 1.0)

        _values = type2cnt.values()
        _values /= np.sum(_values)
        entropy = -1 * np.sum(_values * np.log(_values))
        entropies.append(entropy)

        to_collapse_retval.append((cluster, type2cnt, entropy))

    entropies = np.array(entropies)

    average_entropy = np.average(entropies)

    return singles, to_collapse_retval, average_entropy