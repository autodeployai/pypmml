#
# Copyright (c) 2024 AutoDeployAI
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
from abc import ABC, abstractmethod
import os

class PMMLError(Exception):
    """Base exception of PyPMML"""

class JVMGateway(ABC):
    """Base class of JVM gateway"""
    def __init__(self):
        # Java path
        self.java_path = None

        # JVM options
        self.java_opts = []
        java_opts = os.environ.get("JAVA_OPTS")
        if java_opts:
            self.java_opts.extend(java_opts.split())

        # Classpath
        jars_dir = os.environ["PYPMML_JARS_DIR"] if "PYPMML_JARS_DIR" in os.environ else \
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jars')
        self.classpath = os.path.join(jars_dir, "*")

    @abstractmethod
    def launch_gateway(self, java_opts=None, java_path=None):
        """Launch a `Gateway` in a new Java process.
        :param java_opts: an array of extra options to pass to Java (the classpath
            should be specified using the `classpath` parameter, not `javaopts`.)
        :param java_path: If None, JVM gateway will use $JAVA_HOME/bin/java if $JAVA_HOME
            is defined, otherwise it will use "java".
        """
        if java_opts:
            self.java_opts.extend(java_opts)
        self.java_path = java_path

    def call_java_func(self, func, *args):
        result = func(*args)
        return self.java2py(result)

    @abstractmethod
    def java2py(self, r):
        return r

    @abstractmethod
    def call_java_static_func(self, class_name, func_name, *args):
        return None

    @abstractmethod
    def detach(self, java_object):
        pass

    @abstractmethod
    def shutdown(self):
        pass

    @abstractmethod
    def name(self):
        return "undefined"


class JPypeGateway(JVMGateway):
    """JPype: """
    import jpype
    import jpype.imports
    import importlib
    from jpype import JArray, JObject

    JavaException = None

    def __init__(self):
        super().__init__()
        JPypeGateway._gateway = None

    def launch_gateway(self, java_opts=None, java_path=None):
        """Launch a `Gateway` in a new Java process.
        :param java_opts: an array of extra options to pass to Java (the classpath
            should be specified using the `classpath` parameter, not `javaopts`.)
        :param java_path: If None, JVM gateway will use $JAVA_HOME/bin/java if $JAVA_HOME
            is defined, otherwise it will use "java".
        """
        super().launch_gateway(java_opts=java_opts, java_path=java_path)
        self.jpype.startJVM(*self.java_opts, jvmpath=self.java_path, classpath=self.classpath, convertStrings=True)

    def java2py(self, r):
        if isinstance(r, self.JArray):
            return [self.java2py(x) for x in r]
        elif isinstance(r, self.JObject):
            cls_name = r.getClass().getName()
            if cls_name == 'scala.Some':
                return r.get()
            elif cls_name == 'scala.None$':
                return None
            elif cls_name == 'scala.Enumeration$Val':
                return r.toString()
        return r

    def py2java(self, arg):
        if isinstance(arg, list):
            from java.util import ArrayList
            array_list = ArrayList()
            for x in arg:
                array_list.add(self.py2java(x))
            return array_list
        else:
            return arg

    def call_java_func(self, func, *args):
        java_args = [self.py2java(x) for x in args]
        result = func(*java_args)
        return self.java2py(result)

    def call_java_static_func(self, class_name, func_name, *args):
        try:
            class_obj = self.importlib.import_module(class_name)
            func_obj = getattr(class_obj, func_name)
            return func_obj(*args)
        except self.jpype.JException as e:
            raise PMMLError(e.message())

    def detach(self, java_object):
        pass

    def shutdown(self):
        self.jpype.shutdownJVM()

    def name(self):
        return "JPype"

class Py4jGateway(JVMGateway):
    """Py4j"""
    from py4j.java_collections import JavaArray, JavaList
    from py4j.java_gateway import JavaObject
    from py4j.protocol import Py4JJavaError

    _gateway = None
    _jvm = None

    def __init__(self):
        super().__init__()
        Py4jGateway._gateway = None

    def launch_gateway(self, java_opts=None, java_path=None):
        """Launch a `Gateway` in a new Java process.
        :param java_opts: an array of extra options to pass to Java (the classpath
            should be specified using the `classpath` parameter, not `java_opts`.)
        :param java_path: If None, Py4J will use $JAVA_HOME/bin/java if $JAVA_HOME
            is defined, otherwise it will use "java".
        """
        from py4j.java_gateway import JavaGateway, launch_gateway, GatewayParameters

        super().launch_gateway(java_opts=java_opts, java_path=java_path)
        if Py4jGateway._gateway is None:
            _port = launch_gateway(classpath=self.classpath, javaopts=self.java_opts, java_path=self.java_path, die_on_exit=True)
            Py4jGateway._gateway = JavaGateway(gateway_parameters=GatewayParameters(port=_port, auto_convert=True))
            Py4jGateway._jvm = Py4jGateway._gateway.jvm

    def shutdown(self):
        if Py4jGateway._gateway is not None:
            Py4jGateway._gateway.shutdown()
            Py4jGateway._gateway = None

    def detach(self, java_object):
        Py4jGateway._gateway.detach(java_object)

    def java2py(self, r):
        if isinstance(r, (self.JavaArray, self.JavaList)):
            return [self.java2py(x) for x in r]
        elif isinstance(r, self.JavaObject):
            cls_name = r.getClass().getName()
            if cls_name == 'scala.Some':
                return r.get()
            elif cls_name == 'scala.None$':
                return None
            elif cls_name == 'scala.Enumeration$Val':
                return r.toString()
        return r

    def call_java_static_func(self, class_name, func_name, *args):
        """ Call Java Static Function """
        try:
            class_obj = getattr(self._jvm, class_name)
            func_obj = getattr(class_obj, func_name)
            return func_obj(*args)
        except self.Py4JJavaError as e:
            je = e.java_exception
            raise PMMLError(je.getClass().getSimpleName(), je.getMessage())

    def name(self):
        return "Py4j"