#
# Copyright (c) 2017-2019 AutoDeploy AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
from py4j.protocol import Py4JJavaError

from pypmml.base import JavaModelWrapper, PMMLContext, PmmlError
from pypmml.elements import Header
from pypmml.metadata import Field, OutputField, DataDictionary


class Model(JavaModelWrapper):
    """A PMML model.
    """
    def __init__(self, java_model):
        super(Model, self).__init__(java_model)

    @property
    def version(self):
        """PMML version."""
        return self.call('version')

    @property
    def header(self):
        """The header of this model."""
        return Header(self.call('header'))

    @property
    def dataDictionary(self):
        """The data dictionary of this model."""
        return DataDictionary(self.call('dataDictionary'))

    @property
    def modelElement(self):
        """Model element type."""
        return self.call('modelElement').toString()

    @property
    def functionName(self):
        """
        Describe the kind of mining model, e.g., whether it is intended to be used for clustering or for classification.
        """
        return self.call('functionName')

    @property
    def modelName(self):
        """
        Identifies the model with a unique name in the context of the PMML file.
        This attribute is not required. Consumers of PMML models are free to manage the names of the models at their
        discretion.
        """
        return self.call('modelName')

    @property
    def algorithmName(self):
        """
        The algorithm name is free-type and can be any description for the specific algorithm that produced the model.
        This attribute is for information only.
        """
        return self.call('algorithmName')

    @property
    def inputNames(self):
        """All input names."""
        return self.call('inputNames')

    @property
    def inputFields(self):
        """All input fields."""
        return [Field(x) for x in self.call('inputFields')]

    @property
    def targetName(self):
        """The target name."""
        return self.call('targetName')

    @property
    def targetNames(self):
        """All target names."""
        return self.call('targetNames')

    @property
    def targetField(self):
        """The target field."""
        return [Field(x) for x in self.call('targetField')]

    @property
    def targetFields(self):
        """All target fields."""
        return [Field(x) for x in self.call('targetFields')]

    @property
    def outputNames(self):
        """All output names."""
        return self.call('outputNames')

    @property
    def outputFields(self):
        """All output fields."""
        return [OutputField(x) for x in self.call('outputFields')]

    @property
    def classes(self):
        """The class labels in a classification model."""
        return self.call('classes')

    def setSupplementOutput(self, value):
        self.call('setSupplementOutput', value)
        return self

    def _is_nd_array(self, data):
        try:
            import numpy as np
            return isinstance(data, np.ndarray)
        except ImportError:
            return False

    def _is_pandas_dataframe(self, data):
        try:
            import pandas as pd
            return isinstance(data, pd.DataFrame)
        except ImportError:
            return False

    def _is_pandas_series(self, data):
        try:
            import pandas as pd
            return isinstance(data, pd.Series)
        except ImportError:
            return False

    def predict(self, data):
        """
        Predict values for a given data.

        :param data:
          Support dict, string in JSON, and Series, DataFrame of Pandas
        :return:
          Scoring results in the same format as input data
        """
        if isinstance(data, (dict, str, u"".__class__)):
            return self.call('predict', data)
        else:
            if isinstance(data, list):
                if data:
                    record = data[0]
                    if isinstance(record, list):
                        return [self.call('predict', record) for record in data]
                    else:
                        return self.call('predict', data)
                else:
                    return []
            elif self._is_nd_array(data):
                import numpy as np
                if data.ndim == 1:
                    return self.call('predict', data.tolist())
                elif data.ndim == 2:
                    return [self.call('predict', record.tolist()) for record in data]
                else:
                    raise PmmlError('Max 2 dimensions are supported')            
            elif self._is_pandas_dataframe(data):
                import pandas as pd
                records = data.to_dict('records')
                result = [self.call('predict', record) for record in records]
                return pd.DataFrame.from_records(result)
            elif self._is_pandas_series(data):
                import pandas as pd
                record = data.to_dict()
                result = self.call('predict', record)
                return pd.DataFrame.from_records([result]).iloc[0]
            else:
                raise PmmlError('Data type "{type}" not supported'.format(type=type(data).__name__))

    @classmethod
    def fromFile(cls, name):
        """Load a model from PMML file with given pathname"""
        pc = PMMLContext.getOrCreate()
        try:
            java_model = pc._jvm.org.pmml4s.model.Model.fromFile(name)
            return cls(java_model)
        except Py4JJavaError as e:
            je = e.java_exception
            raise PmmlError(je.getClass().getSimpleName(), je.getMessage())

    @classmethod
    def fromString(cls, s):
        """Load a model from PMML in a string"""
        pc = PMMLContext.getOrCreate()
        try:
            java_model = pc._jvm.org.pmml4s.model.Model.fromString(s)
            return cls(java_model)
        except Py4JJavaError as e:
            je = e.java_exception
            raise PmmlError(je.getClass().getSimpleName(), je.getMessage())

    @classmethod
    def fromBytes(cls, bytes_array):
        """Load a model from PMML in an array of bytes"""
        pc = PMMLContext.getOrCreate()
        try:
            java_model = pc._jvm.org.pmml4s.model.Model.fromBytes(bytes_array)
            return cls(java_model)
        except Py4JJavaError as e:
            je = e.java_exception
            raise PmmlError(je.getClass().getSimpleName(), je.getMessage())

    @classmethod
    def load(cls, f):
        """Load a model from PMML in any formats of readable, a file path, a string,
        or an array of bytes(bytes or bytearray)"""
        model_content = f
        if hasattr(f, 'read') and callable(f.read):
            model_content = f.read()

        if isinstance(model_content, (bytes, bytearray)):
            model_content = model_content.decode('utf-8')

        if isinstance(model_content, (str, u"".__class__)):
            # Check if a file path
            if os.path.exists(model_content):
                model = cls.fromFile(model_content)
            else:
                model = cls.fromString(model_content)
            return model
        else:
            raise PmmlError('Input type "{type}" not supported'.format(type=type(f).__name__))

    @classmethod
    def close(cls):
        """Shutdown the gateway of Py4J"""
        PMMLContext.shutdown()
