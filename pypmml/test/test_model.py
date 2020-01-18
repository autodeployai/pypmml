#
# Copyright (c) 2017-2019 AutoDeploy AI
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest
from unittest import TestCase

import pandas as pd

from pypmml import Model


class ModelTestCase(TestCase):

    def test_from_file(self):
        # The model is from here: http://dmg.org/pmml/pmml_examples/KNIME_PMML_4.1_Examples/single_iris_dectree.xml
        model = Model.fromFile('./resources/models/single_iris_dectree.xml')
        self.assertEqual(model.version, '4.1')

        app = model.header.application
        self.assertEqual(app.name, 'KNIME')
        self.assertEqual(app.version, '2.8.0')

        self.assertEqual(model.modelElement, 'TreeModel')
        self.assertEqual(model.functionName, 'classification')
        self.assertEqual(model.modelName, 'DecisionTree')
        self.assertEqual(model.algorithmName, None)

        self.assertEqual(model.inputNames, ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
        inputFields = model.inputFields
        self.assertEqual(len(inputFields), 4)
        self.assertEqual(inputFields[0].name, 'sepal_length')
        self.assertEqual(inputFields[0].dataType, 'double')
        self.assertEqual(inputFields[0].opType, 'continuous')

        self.assertEqual(model.targetNames, ['class'])
        targetFields = model.targetFields
        self.assertEqual(len(targetFields), 1)
        self.assertEqual(targetFields[0].name, 'class')
        self.assertEqual(targetFields[0].dataType, 'string')
        self.assertEqual(targetFields[0].opType, 'nominal')
        self.assertEqual(model.classes, ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica'])

        self.assertEqual(model.outputNames, ['PredictedValue', 'Probability', 'Probability_Iris-setosa', 'Probability_Iris-versicolor', 'Probability_Iris-virginica', 'Node_ID'])
        outputFields = model.outputFields
        self.assertEqual(outputFields[0].feature, 'predictedValue')
        self.assertEqual(outputFields[1].feature, 'probability')
        self.assertEqual(outputFields[1].value, None)
        self.assertEqual(outputFields[2].feature, 'probability')
        self.assertEqual(outputFields[2].value, 'Iris-setosa')
        self.assertEqual(outputFields[3].feature, 'probability')
        self.assertEqual(outputFields[3].value, 'Iris-versicolor')
        self.assertEqual(outputFields[4].feature, 'probability')
        self.assertEqual(outputFields[4].value, 'Iris-virginica')
        self.assertEqual(outputFields[5].feature, 'entityId')

        # Data in dict
        result = model.predict({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2})
        self.assertEqual(result['PredictedValue'], 'Iris-setosa')
        self.assertEqual(result['Probability'], 1.0)
        self.assertEqual(result['Node_ID'], '1')

        result = model.predict({'sepal_length': 7, 'sepal_width': 3.2, 'petal_length': 4.7, 'petal_width': 1.4})
        self.assertEqual(result['PredictedValue'], 'Iris-versicolor')
        self.assertEqual(result['Probability'], 0.9074074074074074)
        self.assertEqual(result['Node_ID'], '3')

        # Data in json
        result = model.predict('[{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}]')
        self.assertEqual(result, '[{"Probability":1.0,"Probability_Iris-versicolor":0.0,"Probability_Iris-setosa":1.0,"Probability_Iris-virginica":0.0,"PredictedValue":"Iris-setosa","Node_ID":"1"}]')

        result = model.predict('{"columns": ["sepal_length", "sepal_width", "petal_length", "petal_width"], "data": [[7, 3.2, 4.7, 1.4]]}')
        self.assertEqual(result, '{"columns":["PredictedValue","Probability","Probability_Iris-setosa","Probability_Iris-versicolor","Probability_Iris-virginica","Node_ID"],"data":[["Iris-versicolor",0.9074074074074074,0.0,0.9074074074074074,0.09259259259259259,"3"]]}')

        # Data in Series
        result = model.predict(pd.Series({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2}))
        self.assertEqual(result.get('PredictedValue'), 'Iris-setosa')
        self.assertEqual(result.get('Probability'), 1.0)
        self.assertEqual(result.get('Node_ID'), '1')

        # Data in DataFrame
        data = pd.read_csv('./resources/data/Iris.csv')
        result = model.predict(data)
        self.assertEqual(result.iloc[0].get('PredictedValue'), 'Iris-setosa')
        self.assertEqual(result.iloc[0].get('Probability'), 1.0)
        self.assertEqual(result.iloc[0].get('Node_ID'), '1')

        # Shutdown the gateway
        Model.close()

    def test_load(self):
        file_path = './resources/models/single_iris_dectree.xml'
        self.assertTrue(Model.load(file_path) is not None)

        with open(file_path, 'rb') as f:
            self.assertTrue(Model.load(f) is not None)

        with open(file_path) as f:
            self.assertTrue(Model.load(f) is not None)

        with open(file_path, 'rb') as f:
            s = f.read()
            self.assertTrue(Model.load(s) is not None)
            s = bytearray(s)
            self.assertTrue(Model.load(s) is not None)

        with open(file_path) as f:
            s = f.read()
            self.assertTrue(Model.load(s) is not None)


if __name__ == '__main__':
    unittest.main()
