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


class Application(JavaModelWrapper):
    @property
    def name(self):
        return self.call('name')

    @property
    def version(self):
        return self.call('version')


class Header(JavaModelWrapper):

    @property
    def copyright(self):
        return self.call('copyright')

    @property
    def description(self):
        return self.call('description')

    @property
    def modelVersion(self):
        return self.call('modelVersion')

    @property
    def application(self):
        app = self.call('application')
        return Application(app) if app is not None else None

