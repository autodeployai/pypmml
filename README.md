# PyPMML

_PyPMML_ is a Python PMML scoring library, it really is the Python API for [PMML4S](https://github.com/autodeployai/pmml4s).

## Prerequisites
 - Java >= 8
 - Python 2.7 or >= 3.5

## Dependencies
  - [Py4J](https://www.py4j.org/)
  - or
  - [JPype](https://www.jpype.org/)

## Installation

```bash
pip install pypmml
```

Or install the latest version from github:

```bash
pip install --upgrade git+https://github.com/autodeployai/pypmml.git
```

## Usage
1. Load model from various sources, e.g. readable, file path, string, or an array of bytes.

    ```python
    from pypmml import Model
    
    # The model is from http://dmg.org/pmml/pmml_examples/KNIME_PMML_4.1_Examples/single_iris_dectree.xml
    model = Model.load('single_iris_dectree.xml')
    ```

2. Call `predict(data)` to predict new values that can be in different types, e.g. dict, list, json, ndarray of NumPy, Series or DataFrame of Pandas.

    * **`data` in dict:**

    ```python
    >>> model.predict({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2})
    {'probability_Iris-setosa': 1.0, 'probability_Iris-versicolor': 0.0, 'probability': 1.0, 'predicted_class': 'Iris-setosa', 'probability_Iris-virginica': 0.0, 'node_id': '1'}
    ```

    * **`data` in list:** 
    
    NOTE: the order of values must match the input names, and the order of results always matches the output names.

    ```python
    >>> model.inputNames
    ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    >>> model.predict([5.1, 3.5, 1.4, 0.2])
    ['Iris-setosa', 1.0, 1.0, 0.0, 0.0, '1']
    >>> model.outputNames
    ['predicted_class', 'probability', 'probability_Iris-setosa', 'probability_Iris-versicolor', 'probability_Iris-virginica', 'node_id']
    ```
    
    * **`data` in `records` json:**

    ```python
    >>> model.predict('[{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}]')
    [{"probability":1.0,"probability_Iris-versicolor":0.0,"probability_Iris-setosa":1.0,"probability_Iris-virginica":0.0,"predicted_class":"Iris-setosa","node_id":"1"}]
    ```

    * **`data` in `split` json:**
 
    ```python
    >>> model.predict('{"columns": ["sepal_length", "sepal_width", "petal_length", "petal_width"], "data": [[5.1, 3.5, 1.4, 0.2]]}')
    {"columns":["predicted_class","probability","probability_Iris-setosa","probability_Iris-versicolor","probability_Iris-virginica","node_id"],"data":[["Iris-setosa",1.0,1.0,0.0,0.0,"1"]]}
    ```

    * **`data` in ndarray of NumPy:**

    NOTE: as the list above, the order of ndarray values must match the input names, and the order of results always matches the output names.
    ```python
    >>> import numpy as np
    >>> model.predict(np.array([5.1, 3.5, 1.4, 0.2]))
    ['Iris-setosa', 1.0, 1.0, 0.0, 0.0, '1']
    >>> 
    >>> model.predict(np.array([[5.1, 3.5, 1.4, 0.2], [7, 3.2, 4.7, 1.4]]))
    [['Iris-setosa', 1.0, 1.0, 0.0, 0.0, '1'], ['Iris-versicolor', 0.9074074074074074, 0.0, 0.9074074074074074, 0.09259259259259259, '3']]
    ```

    * **`data` in Series of Pandas:**
    
    ```python
    >>> import pandas as pd
    >>> model.predict(pd.Series({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2}))
    node_id                                  1
    predicted_class                Iris-setosa
    probability                              1
    probability_Iris-setosa                  1
    probability_Iris-versicolor              0
    probability_Iris-virginica               0
    Name: 0, dtype: object
    ```

    * **`data` in DataFrame of Pandas:**

    ```python
    >>> import pandas as pd
    >>> data = pd.read_csv('Iris.csv') # The data is from here: http://dmg.org/pmml/pmml_examples/Iris.csv
    >>> model.predict(data)
    node_id predicted_class  probability  probability_Iris-setosa  probability_Iris-versicolor  probability_Iris-virginica
    0         1     Iris-setosa     1.000000                      1.0                     0.000000                    0.000000
    1         1     Iris-setosa     1.000000                      1.0                     0.000000                    0.000000
    2         1     Iris-setosa     1.000000                      1.0                     0.000000                    0.000000
    3         1     Iris-setosa     1.000000                      1.0                     0.000000                    0.000000
    4         1     Iris-setosa     1.000000                      1.0                     0.000000                    0.000000
    ..      ...             ...          ...                      ...                          ...                         ...
    145      10  Iris-virginica     0.978261                      0.0                     0.021739                    0.978261
    146      10  Iris-virginica     0.978261                      0.0                     0.021739                    0.978261
    147      10  Iris-virginica     0.978261                      0.0                     0.021739                    0.978261
    148      10  Iris-virginica     0.978261                      0.0                     0.021739                    0.978261
    149      10  Iris-virginica     0.978261                      0.0                     0.021739                    0.978261
    ```
## Support Java gateways
PyPMML supports both backends access to Java from Python: "py4j" and "jpype", `Py4j` is used by default, you can call the following code to switch to `jpype` before loading models:
```python
from pypmml import PMMLContext

PMMLContext.getOrCreate(gateway="jpype")
```

## Use PMML in Scala or Java
See the [PMML4S](https://github.com/autodeployai/pmml4s) project. _PMML4S_ is a PMML scoring library for Scala. It provides both Scala and Java Evaluator API for PMML.

## Use PMML in Spark
See the [PMML4S-Spark](https://github.com/autodeployai/pmml4s-spark) project. _PMML4S-Spark_ is a PMML scoring library for Spark as SparkML Transformer.

## Use PMML in PySpark
See the [PyPMML-Spark](https://github.com/autodeployai/pypmml-spark) project. _PyPMML-Spark_ is a Python PMML scoring library for PySpark as SparkML Transformer, it really is the Python API for PMML4s-Spark.

## Deploy PMML as REST API
See the [AI-Serving](https://github.com/autodeployai/ai-serving) project. _AI-Serving_ is serving AI/ML models in the open standard formats PMML and ONNX with both HTTP (REST API) and gRPC endpoints.

## Support
If you have any questions about the _PyPMML_ library, please open issues on this repository.

Feedback and contributions to the project, no matter what kind, are always very welcome. 

## License
_PyPMML_ is licensed under [APL 2.0](http://www.apache.org/licenses/LICENSE-2.0).
