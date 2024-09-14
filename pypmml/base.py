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

from threading import RLock
from .jvm import JVMGateway

class PMMLContext(object):
    _gateway: JVMGateway = None
    _active_pmml_context = None
    _lock = RLock()

    def __init__(self, gateway_instance=None, gateway="py4j", java_opts=None, java_path=None):
        PMMLContext._ensure_initialized(
            self,
            gateway_instance=gateway_instance,
            gateway=gateway,
            java_opts=java_opts,
            java_path=java_path)

    @classmethod
    def _ensure_initialized(cls, instance, gateway_instance=None, gateway="py4j", java_opts=None, java_path=None):
        """
        Checks whether a Gateway of JVM is initialized or not.
        """
        with PMMLContext._lock:
            if not PMMLContext._gateway:
                PMMLContext._gateway = gateway_instance or cls.launch_gateway(
                    gateway=gateway, java_opts=java_opts, java_path=java_path
                )

            if instance:
                if PMMLContext._active_pmml_context and PMMLContext._active_pmml_context != instance:
                    # Raise error if there is already a running PMML context
                    raise ValueError("Cannot run multiple PMMLContexts at once")
                else:
                    PMMLContext._active_pmml_context = instance

    @classmethod
    def getOrCreate(cls, gateway="py4j", java_opts=None, java_path=None) -> 'PMMLContext':
        """
        Get or instantiate a PMMLContext and register it as a singleton object.
        :param java_opts: an array of extra options to pass to Java (the classpath
            should be specified using the `classpath` parameter, not `java_opts`.)
        :param java_path: If None, JVM will use $JAVA_HOME/bin/java if $JAVA_HOME
            is defined, otherwise it will use "java".
        :param gateway: JVM gateway engine, support one of ["py4j", "jpype"]
        """
        with PMMLContext._lock:
            if PMMLContext._active_pmml_context is None:
                PMMLContext(gateway=gateway, java_opts=java_opts, java_path=java_path)
            return PMMLContext._active_pmml_context

    @classmethod
    def launch_gateway(cls, gateway="py4j", java_opts=None, java_path=None) -> 'JVMGateway':
        """Launch a `Gateway` in a new Java process.
        :param gateway: JVM gateway engine, support one of ["py4j", "jpype"]
        :param java_opts: an array of extra options to pass to Java (the classpath
            should be specified using the `classpath` parameter, not `java_opts`.)
        :param java_path: If None, JVM will use $JAVA_HOME/bin/java if $JAVA_HOME
            is defined, otherwise it will use "java".
        :return: An object of `Gateway`
        """
        if isinstance(gateway, str) and gateway.lower() == "jpype":
            from .jvm import JPypeGateway
            jvm_gateway = JPypeGateway()
        else:
            from .jvm import Py4jGateway
            jvm_gateway = Py4jGateway()
        jvm_gateway.launch_gateway(java_opts=java_opts, java_path=java_path)
        return jvm_gateway

    @classmethod
    def shutdown(cls):
        """Shuts down the :class:`GatewayClient` and the
           :class:`CallbackServer <py4j.java_callback.CallbackServer>`.
        """
        with PMMLContext._lock:
            if PMMLContext._gateway:
                PMMLContext._gateway.shutdown()
            PMMLContext._gateway = None
            PMMLContext._active_pmml_context = None

    def call_java_static_func(self, class_name, func_name, *args):
        return self._gateway.call_java_static_func(class_name, func_name, *args)

    def call_java_func(self, func, *args):
        return self._gateway.call_java_func(func, *args)

    def detach(self, java_model):
        if self._gateway:
            self._gateway.detach(java_model)

    @classmethod
    def gateway(cls):
        return cls._gateway.name() if cls._gateway is not None else None

class JavaModelWrapper(object):
    """
    Wrapper for the model in JVM
    """
    def __init__(self, java_model):
        self._pc = PMMLContext.getOrCreate()
        self._java_model = java_model

    def __del__(self):
        if self._pc:
            self._pc.detach(self._java_model)

    def call(self, name, *args):
        return self._pc.call_java_func(getattr(self._java_model, name), *args)

    def __str__(self):
        return self.call('toString')

