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
        inputs = model.inputFields
        self.assertEqual(len(inputs), 4)
        self.assertEqual(inputs[0].name, 'sepal_length')
        self.assertEqual(inputs[0].dataType, 'double')
        self.assertEqual(inputs[0].opType, 'continuous')

        self.assertEqual(model.targetNames, ['class'])
        targets = model.targetFields
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0].name, 'class')
        self.assertEqual(targets[0].dataType, 'string')
        self.assertEqual(targets[0].opType, 'nominal')
        self.assertEqual(model.classes, ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica'])

        self.assertEqual(model.outputNames, ['predicted_class', 'probability', 'probability_Iris-setosa', 'probability_Iris-versicolor', 'probability_Iris-virginica', 'node_id'])
        outputs = model.outputFields
        self.assertEqual(outputs[0].feature, 'predictedValue')
        self.assertEqual(outputs[1].feature, 'probability')
        self.assertEqual(outputs[1].value, None)
        self.assertEqual(outputs[2].feature, 'probability')
        self.assertEqual(outputs[2].value, 'Iris-setosa')
        self.assertEqual(outputs[3].feature, 'probability')
        self.assertEqual(outputs[3].value, 'Iris-versicolor')
        self.assertEqual(outputs[4].feature, 'probability')
        self.assertEqual(outputs[4].value, 'Iris-virginica')
        self.assertEqual(outputs[5].feature, 'entityId')

        # Data in dict
        result = model.predict({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2})
        self.assertEqual(result['predicted_class'], 'Iris-setosa')
        self.assertEqual(result['probability'], 1.0)
        self.assertEqual(result['node_id'], '1')

        result = model.predict({'sepal_length': 7, 'sepal_width': 3.2, 'petal_length': 4.7, 'petal_width': 1.4})
        self.assertEqual(result['predicted_class'], 'Iris-versicolor')
        self.assertEqual(result['probability'], 0.9074074074074074)
        self.assertEqual(result['node_id'], '3')

        # Data in json
        result = model.predict('[{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}]')
        self.assertEqual(result, '[{"node_id":"1","probability_Iris-setosa":1.0,"predicted_class":"Iris-setosa","probability_Iris-virginica":0.0,"probability_Iris-versicolor":0.0,"probability":1.0}]')

        result = model.predict('{"columns": ["sepal_length", "sepal_width", "petal_length", "petal_width"], "data": [[7, 3.2, 4.7, 1.4]]}')
        self.assertEqual(result, '{"columns":["predicted_class","probability","probability_Iris-setosa","probability_Iris-versicolor","probability_Iris-virginica","node_id"],"data":[["Iris-versicolor",0.9074074074074074,0.0,0.9074074074074074,0.09259259259259259,"3"]]}')

        # Data in list
        result = model.predict([5.1, 3.5, 1.4, 0.2])
        self.assertEqual(result[0], 'Iris-setosa')
        self.assertEqual(result[1], 1.0)
        self.assertEqual(result[2], 1.0)
        self.assertEqual(result[3], 0.0)
        self.assertEqual(result[4], 0.0)
        self.assertEqual(result[5], '1')

        # Data in list of list
        result = model.predict([[5.1, 3.5, 1.4, 0.2], [7, 3.2, 4.7, 1.4]])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 'Iris-setosa')
        self.assertEqual(result[0][1], 1.0)
        self.assertEqual(result[0][2], 1.0)
        self.assertEqual(result[0][3], 0.0)
        self.assertEqual(result[0][4], 0.0)
        self.assertEqual(result[0][5], '1')
        self.assertEqual(result[1][0], 'Iris-versicolor')
        self.assertEqual(result[1][1], 0.9074074074074074)
        self.assertEqual(result[1][2], 0.0)
        self.assertEqual(result[1][3], 0.9074074074074074)
        self.assertEqual(result[1][4], 0.09259259259259259)
        self.assertEqual(result[1][5], '3')

        # Data in numpy

        # Shutdown the gateway
        Model.close()

    def test_pandas(self):
        try:
            import pandas as pd
            model = Model.load('./resources/models/single_iris_dectree.xml')

            # Data in Series
            result = model.predict(pd.Series({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2}))
            self.assertEqual(result.get('predicted_class'), 'Iris-setosa')
            self.assertEqual(result.get('probability'), 1.0)
            self.assertEqual(result.get('node_id'), '1')

            # Data in DataFrame
            data = pd.read_csv('./resources/data/Iris.csv')
            result = model.predict(data)
            self.assertEqual(result.iloc[0].get('predicted_class'), 'Iris-setosa')
            self.assertEqual(result.iloc[0].get('probability'), 1.0)
            self.assertEqual(result.iloc[0].get('node_id'), '1')
        except ImportError:
            pass

    def test_numpy(self):
        try:
            import numpy as np
            model = Model.load('./resources/models/single_iris_dectree.xml')

            # Data in 1-D
            result = model.predict(np.array([5.1, 3.5, 1.4, 0.2]))
            self.assertEqual(result[0], 'Iris-setosa')
            self.assertEqual(result[1], 1.0)
            self.assertEqual(result[2], 1.0)
            self.assertEqual(result[3], 0.0)
            self.assertEqual(result[4], 0.0)
            self.assertEqual(result[5], '1')

            # Data in 2-D
            result = model.predict(np.array([[5.1, 3.5, 1.4, 0.2], [7, 3.2, 4.7, 1.4]]))
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0][0], 'Iris-setosa')
            self.assertEqual(result[0][1], 1.0)
            self.assertEqual(result[0][2], 1.0)
            self.assertEqual(result[0][3], 0.0)
            self.assertEqual(result[0][4], 0.0)
            self.assertEqual(result[0][5], '1')
            self.assertEqual(result[1][0], 'Iris-versicolor')
            self.assertEqual(result[1][1], 0.9074074074074074)
            self.assertEqual(result[1][2], 0.0)
            self.assertEqual(result[1][3], 0.9074074074074074)
            self.assertEqual(result[1][4], 0.09259259259259259)
            self.assertEqual(result[1][5], '3')

        except ImportError:
            pass

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


