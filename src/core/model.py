# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.


class ModelInput:

    def __init__(self):
        pass

class ModelResult:

    def __init__(self):
        pass

class Model:

    model_input = None
    model_result = None

    def __init__(self, model_input):
        self.model_input = model_input

    def setObjective(self, *args):
        pass

    def setConstraints(self, *args):
        pass

    def setHints(self, *args):
        pass

    def solve(self, *args):
        pass

    def setModelInput(self, model_input):
        self.model_input = model_input

    def getModelResult():
        return self.model_result

    def getObjectiveValue():
        pass