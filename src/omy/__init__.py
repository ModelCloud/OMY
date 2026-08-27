# Copyright 2020 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
OMY (Open Model Yard) is a drop-in distribution of the transformers library.

`import omy` is an alias for `import transformers`; all public APIs, submodules,
and the CLI remain accessible under the original `transformers` namespace as well.
"""

import sys

import transformers


__version__ = transformers.__version__

# Make `import omy` and `import omy as transformers` behave exactly like `import transformers`.
sys.modules[__name__] = transformers
