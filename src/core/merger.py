# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from .structure import *

class ResultMerger:

    def __init__(self):
        pass

    def merge(self, model_input, model_result_list, optimized=False):
        """Function that merges the result from a list of partial results.
           
        Args:
            model_input: the object that stores the model input.
            model_result_list: the list of partial results in DataFrame.

        Returns:
            model_result: the final model result after merged in DataFrame.

        """

        if not optimized:
            return pd.concat(model_result_list)
        else:
            return self.optimize(model_input, model_result_list)

        

    def optimize(self, model_input, model_result_list):
        """Function that further optimizes the result from a list of partial results.
           
        Args:
            model_input: the object that stores the model input.
            model_result_list: the list of partial results in DataFrame.

        Returns:
            model_result: the model result after optimized in DataFrame.

        """
        pass
