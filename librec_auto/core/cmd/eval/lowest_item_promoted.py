class LowestItemPromoted(ListBasedMetric):
    def __init__(self, params: dict, conf: ConfigCmd, test_data: np.array,
                 result_data: np.array, output_file, user_file=None) -> None:
        # print(params)
        super().__init__(params, conf, test_data, result_data, output_file)
        self._user_file = user_file
        self._name = 'lowest_item'

    def evaluate_user(self, test_user_data: np.array,
                      result_user_data: np.array) -> float:
        rec_num = int(self._params['list_size'])
        # This is where I need original results
        # modified from https://github.com/nasimsonboli/OFAiR/blob/main/source%20code/OFAiR_Evaluation.ipynb
        idealOrder = test_user_data
        for element in reversed(original_list):
            if element in reranked_list:
                if element in features[0]:
                    result = original_list.index(element)

        if self._user_file is not None:
            file.write(result)
        return result

    def postprocessing(self):
        print(np.average(self._values))
        return np.average(self._values)


def read_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='My custom metric')
    parser.add_argument('--conf', help='Path to config file')
    parser.add_argument('--test', help='Path to test.')
    parser.add_argument('--result', help='Path to results.')
    parser.add_argument('--output-file', help='The output pickle file.')

    # Custom params defined in the config go here
    parser.add_argument('--original_list_size', help='Size of the list for NDCG.')
    # parser.add_argument('--user_output')

    input_args = parser.parse_args()
    print(vars(input_args))
    return vars(input_args)


def read_data_from_file(file_name, delimiter='\t'):
    d = []
    print(file_name)
    with open(file_name, "r") as f:
        for line in f:
            split_line = line.split(delimiter)
            split_line[1] = int(split_line[1])
            d.append(split_line)

    d = np.array(d)
    return d


if __name__ == '__main__':
    args = read_args()
    # print(args)
    # parse_protected
    # protected_feature_file can be parsed here

    config = read_config_file(args['conf'], '.')

    params = {'list_size': args['list_size']}

    test_data = read_data_from_file(
        args['test']
    )
    result_data = read_data_from_file(
        args['result'],
        delimiter=','
    )

    user_output_file = 'DEBUG_user_output.txt'

    print("Creating metric")

    if "user_output" in args:
        with open(user_output_file, 'w') as file:
            custom = NdcgMetric(params, config, test_data, result_data,
                                args['output_file'], file)
            custom.evaluate()
    else:

        custom = NdcgMetric(params, config, test_data, result_data,
                            args['output_file'])
        custom.evaluate()

    print("applying metric")