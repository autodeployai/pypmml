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
from os import path
from threading import RLock

from py4j.java_collections import JavaArray
from py4j.java_gateway import JavaObject, JavaGateway, launch_gateway, GatewayParameters


def _java2py(r):
    if isinstance(r, JavaArray):
        return [_java2py(x) for x in r]
    elif isinstance(r, JavaObject):
        cls_name = r.getClass().getName()
        if cls_name == 'scala.Some':
            return r.get()
        elif cls_name == 'scala.None$':
            return None
        elif cls_name == 'scala.Enumeration$Val':
            return r.toString()
    return r


def call_java_func(func, *args):
    """ Call Java Function """
    return _java2py(func(*args))


class PMMLContext(object):
    _gateway = None
    _jvm = None
    _active_pmml_context = None
    _lock = RLock()

    def __init__(self, gateway=None):
        PMMLContext._ensure_initialized(self, gateway=gateway)

    @classmethod
    def _ensure_initialized(cls, instance, gateway=None):
        """
        Checks whether a Gateway of py4j is initialized or not.
        """
        with PMMLContext._lock:
            if not PMMLContext._gateway:
                PMMLContext._gateway = gateway or cls.launch_gateway()
                PMMLContext._jvm = PMMLContext._gateway.jvm

            if instance:
                if PMMLContext._active_pmml_context and PMMLContext._active_pmml_context != instance:
                    # Raise error if there is already a running PMML context
                    raise ValueError("Cannot run multiple PMMLContexts at once")
                else:
                    PMMLContext._active_pmml_context = instance

    @classmethod
    def getOrCreate(cls):
        """
        Get or instantiate a PMMLContext and register it as a singleton object.
        """
        with PMMLContext._lock:
            if PMMLContext._active_pmml_context is None:
                PMMLContext()
            return PMMLContext._active_pmml_context

    @classmethod
    def launch_gateway(cls):
        jars_dir = os.environ["PYPMML_JARS_DIR"] if "PYPMML_JARS_DIR" in os.environ else \
            path.join(path.dirname(path.abspath(__file__)), 'jars')
        launch_classpath = path.join(jars_dir, "*")

        _port = launch_gateway(classpath=launch_classpath, die_on_exit=True)
        gateway = JavaGateway(
            gateway_parameters=GatewayParameters(port=_port,
                                                 auto_convert=True))
        return gateway

    @classmethod
    def shutdown(cls):
        """Shuts down the :class:`GatewayClient` and the
           :class:`CallbackServer <py4j.java_callback.CallbackServer>`.
        """
        with PMMLContext._lock:
            if PMMLContext._gateway:
                PMMLContext._gateway.shutdown()
            PMMLContext._gateway = None
            PMMLContext._jvm = None
            PMMLContext._active_pmml_context = None


class PmmlError(Exception):
    """Base exception of PyPMML"""


class JavaModelWrapper(object):
    """
    Wrapper for the model in JVM
    """
    def __init__(self, java_model):
        self._pc = PMMLContext.getOrCreate()
        self._java_model = java_model

    def __del__(self):
        if self._pc._gateway:
            self._pc._gateway.detach(self._java_model)

    def call(self, name, *a):
        return call_java_func(getattr(self._java_model, name), *a)

    def __str__(self):
        return self.call('toString')

