# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys
from unittest.mock import MagicMock
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../examples'))
sys.path.insert(0, os.path.abspath('../../examples/PositionController'))
sys.path.insert(0, os.path.abspath('../../examples/PositionController/json'))
sys.path.insert(0, os.path.abspath('../../examples/GazeController'))

# Mock yarp and other unavailable dependencies
MOCK_MODULES = ["yarp"]
sys.modules.update((mod_name, MagicMock()) for mod_name in MOCK_MODULES)

# Add project directories to the path
sys.path.insert(0, os.path.abspath("../"))  # Adjust if necessary
# -- Project information -----------------------------------------------------

project = "PyiCub"
copyright = "2024, Davide De Tommaso"
author = "Davide De Tommaso, Enrico Piacenti"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_rtd_theme",
    "sphinx.ext.intersphinx",
]

autodoc_typehints = "signature"

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "member-order": "bysource",
}

autosummary_generate = True

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_rtype = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_js_files = ["custom.js"]
html_css_files = ["custom.css"]


master_doc = "index"
