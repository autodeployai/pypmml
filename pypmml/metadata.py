#
# Copyright (c) 2017-2024 AutoDeployAI
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

from pypmml.base import JavaModelWrapper


class Field(JavaModelWrapper):

    def __init__(self, java_model):
        super(Field, self).__init__(java_model)

    @property
    def name(self):
        return self.call('name')

    @property
    def displayName(self):
        return self.call('displayName')

    @property
    def dataType(self):
        return self.call('dataType').toString()

    @property
    def opType(self):
        return self.call('opType').toString()

    @property
    def valuesAsString(self):
        return self.call('valuesAsString')


class OutputField(Field):

    def __init__(self, java_model):
        super(Field, self).__init__(java_model)

    @property
    def feature(self):
        return self.call('feature')

    @property
    def targetField(self):
        return self.call('targetField')

    @property
    def value(self):
        obj = self.call('value')
        if obj is not None:
            return DataVal(obj).toVal
        else:
            return None

    @property
    def ruleFeature(self):
        return self.call('ruleFeature').toString()

    @property
    def algorithm(self):
        return self.call('algorithm').toString()

    @property
    def rank(self):
        return self.call('rank')


class DataDictionary(JavaModelWrapper):
    def __init__(self, java_model):
        super(DataDictionary, self).__init__(java_model)

    @property
    def fields(self):
        return [Field(x) for x in self.call('fields')]

    @property
    def fieldNames(self):
        return self.call('fieldNames')

    def get(self, name):
        fld = self.get(name)
        return Field(fld) if fld is not None else None


class DataVal(JavaModelWrapper):
    def __init__(self, java_model):
        super(DataVal, self).__init__(java_model)

    @property
    def toVal(self):
        return self.call('toVal')
