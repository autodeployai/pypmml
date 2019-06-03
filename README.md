# PyPMML

_PyPMML_ is the Python API for [PMML4S](https://github.com/autodeployai/pmml4s).

## Prerequisites
 - Java >= 1.8
 - Python 2.7 or >= 3.5

## Dependencies
  - Py4J
  - Pandas (optional)
  
## Installation

```bash
pip install pypmml
```

Or install the latest version from github:

```bash
pip install --upgrade git+https://github.com/autodeployai/pypmml.git
```

## Usage
1. Load model from various sources, e.g. filename, string, or array of bytes.

    ```python
    from pypmml import Model
    
    # The model is from http://dmg.org/pmml/pmml_examples/KNIME_PMML_4.1_Examples/single_iris_dectree.xml
    model = Model.fromFile('single_iris_dectree.xml')
    ```

2. Call `predict(data)` to predict new values that can be in different types, e.g. dict, json, Series or DataFrame of Pandas.

    ```python
    # data in dict
    result = model.predict({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2})
     >>> print(result)
    {'Probability': 1.0, 'Node_ID': '1', 'Probability_Iris-virginica': 0.0, 'Probability_Iris-setosa': 1.0, 'Probability_Iris-versicolor': 0.0, 'PredictedValue': 'Iris-setosa'}
    
    # data in 'records' json
    result = model.predict('[{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}]')
     >>> print(result)
    [{"Probability":1.0,"Probability_Iris-versicolor":0.0,"Probability_Iris-setosa":1.0,"Probability_Iris-virginica":0.0,"PredictedValue":"Iris-setosa","Node_ID":"1"}]
 
    # data in 'split' json
    result = model.predict('{"columns": ["sepal_length", "sepal_width", "petal_length", "petal_width"], "data": [[5.1, 3.5, 1.4, 0.2]]}')
     >>> print(result)
    {"columns":["PredictedValue","Probability","Probability_Iris-setosa","Probability_Iris-versicolor","Probability_Iris-virginica","Node_ID"],"data":[["Iris-setosa",1.0,1.0,0.0,0.0,"1"]]}
    ```

    How to work with Pandas
    
    ```python
    import pandas as pd
    
    # data in Series
    result = model.predict(pd.Series({'sepal_length': 5.1, 'sepal_width': 3.5, 'petal_length': 1.4, 'petal_width': 0.2}))
    >>> print(result)
    Node_ID                                  1
    PredictedValue                 Iris-setosa
    Probability                              1
    Probability_Iris-setosa                  1
    Probability_Iris-versicolor              0
    Probability_Iris-virginica               0
    Name: 0, dtype: object
    
    # The data is from here: http://dmg.org/pmml/pmml_examples/Iris.csv
    data = pd.read_csv('Iris.csv')
    
    # data in DataFrame
    result = model.predict(data)
     >>> print(result)
        Node_ID   PredictedValue  Probability  Probability_Iris-setosa  Probability_Iris-versicolor  Probability_Iris-virginica
    0         1      Iris-setosa     1.000000                      1.0                     0.000000                    0.000000
    1         1      Iris-setosa     1.000000                      1.0                     0.000000                    0.000000
    ..      ...              ...          ...                      ...                          ...                         ...
    148      10   Iris-virginica     0.978261                      0.0                     0.021739                    0.978261
    149      10   Iris-virginica     0.978261                      0.0                     0.021739                    0.978261
    
    [150 rows x 6 columns]
    ```

3. Shutdown the gateway of Py4J to free resources.

    ```python
    Model.close()
    ```

## Use in PySpark
See the [PyPMML-Spark](https://github.com/autodeployai/pypmml-spark) project.

## Support
If you have any questions about the _PyPMML_ library, please open issues on this repository.

Feedback and contributions to the project, no matter what kind, are always very welcome. 

## License
_PyPMML_ is licensed under [APL 2.0](http://www.apache.org/licenses/LICENSE-2.0).
