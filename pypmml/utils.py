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

def is_nd_array(data):
    try:
        import numpy as np
        return isinstance(data, np.ndarray)
    except ImportError:
        return False


def is_pandas_dataframe(data):
    try:
        import pandas as pd
        return isinstance(data, pd.DataFrame)
    except ImportError:
        return False


def is_pandas_series(data):
    try:
        import pandas as pd
        return isinstance(data, pd.Series)
    except ImportError:
        return False
