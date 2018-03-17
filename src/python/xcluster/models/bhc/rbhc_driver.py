from rbhc import rbhc
from dists import NormalInverseWishart
import numpy as np
import sys
import time


def load_data(filename, num_points=None):
    point_ids = []
    cluster_ids = []
    feature_vectors = []

    with open(filename, 'r') as f:
        if num_points == None:
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


def generate_tree_output(filename, rbhc_tree):
    with open(filename, 'w') as f:
        pass


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

        num_dims = feature_vectors_np.shape[1]
        mean = np.mean(feature_vectors_np, axis=0)
        variance = np.var(feature_vectors_np, axis=0)
        cov = np.zeros((num_dims, num_dims))
        row, col = np.diag_indices(cov.shape[0])
        cov[row, col] = variance

        niw = NormalInverseWishart(nu_0=num_dims + 1, mu_0=mean, kappa_0=1, lambda_0=cov)
        start_time = time.time()
        rbhc_tree = rbhc(data=feature_vectors_np, data_model=niw, point_ids=point_ids, cluster_ids=cluster_ids,
                        verbose=False, sub_size=2)

        print('assignments', rbhc_tree.assignments)
        print('assignments length', len(rbhc_tree.assignments))
        print('nodes length', len(rbhc_tree.nodes))
        for node in rbhc_tree.nodes:
            print(rbhc_tree.nodes[node])
        end_time = time.time()
        running_time = end_time - start_time
        output_time(output_directory + '/running_time.txt', dataset_name, running_time)
        # generate_tree_output(output_directory + '/tree.tsv', rbhc_tree)
    else:
        print('Incorrect number of arguments supplied.')


if __name__ == '__main__':
    main()
