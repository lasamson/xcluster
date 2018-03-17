from bhc import bhc
from dists import NormalInverseWishart
import numpy as np
import sys
import time


def load_data(filename, num_points=None):
    point_ids = []
    cluster_ids = []
    feature_vectors = []

    with open(filename, 'r') as f:
        if num_points is None:
            num_points = sys.maxsize
        for idx, line in enumerate(f):
            if idx < num_points:
                parts = line.strip().split('\t')
                if len(parts) < 2:
                    print('Line should have point id and cluster id')
                point_ids.append(parts[0])
                cluster_ids.append(parts[1])
                feature_vectors.append([float(x) for x in parts[2:]])
            else:
                break

    return point_ids, cluster_ids, feature_vectors


def generate_tree_output(filename, bhc_tree):
    with open(filename, 'w') as f:
        open_list = [(None, bhc_tree.root_node)]
        while open_list:
            cur_parent, cur_node = open_list.pop(0)
            if cur_parent == None:
                f.write('{}\tNone\tNone\n'.format(cur_node.id))
                open_list.append((cur_node, cur_node.left_child))
                open_list.append((cur_node, cur_node.right_child))
            else:
                if (cur_node.left_child is None and cur_node.right_child is None):
                    f.write('{}\t{}\t{}\n'.format(cur_node.point_id, cur_parent.id, cur_node.cluster_id))
                else:
                    f.write('{}\t{}\tNone\n'.format(cur_node.id, cur_parent.id))
                    open_list.append((cur_node, cur_node.left_child))
                    open_list.append((cur_node, cur_node.right_child))


def output_time(filename, dataset_name, running_time):
    with open(filename, 'w') as f:
        f.write('BHC-covariance\t{}\t{}\n'.format(dataset_name, running_time))


def main():
    if len(sys.argv) == 4:
        dataset_name = sys.argv[1]
        input_data = sys.argv[2]
        output_directory = sys.argv[3]
        point_ids, cluster_ids, feature_vectors = load_data(input_data)
        feature_vectors_np = np.array([np.array(dp) for dp in feature_vectors])

        num_points = feature_vectors_np.shape[0]
        num_dims = feature_vectors_np.shape[1]
        mean = np.mean(feature_vectors_np, axis=0)
        variance = np.var(feature_vectors_np, axis=0)
        for idx, var in enumerate(variance):
            variance[idx] = var + 1e-14
        cov = np.zeros((num_dims, num_dims))
        row, col = np.diag_indices(cov.shape[0])
        cov[row, col] = variance

        print (cov)

        niw = NormalInverseWishart(nu_0=num_dims + 1, mu_0=mean, kappa_0=1, lambda_0=cov)
        start_time = time.time()
        bhc_tree = bhc(data=feature_vectors_np, data_model=niw, point_ids=point_ids, cluster_ids=cluster_ids,
                       verbose=True)
        end_time = time.time()
        running_time = end_time - start_time
        output_time(output_directory + '/running_time.txt', dataset_name, running_time)
        generate_tree_output(output_directory + '/tree.tsv', bhc_tree)
    else:
        print('Incorrect number of arguments supplied.')


if __name__ == '__main__':
    main()
