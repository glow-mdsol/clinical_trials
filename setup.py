import codecs
import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="clinical_trials",
    version=find_version("clinical_trials", "__init__.py"),
    packages=["clinical_trials", "tests"],
    install_requires=["requests", "glom", "xmlschema"],
    url="https://github.com/glow-mdsol/clinical_trials",
    license="MIT",
    author="glow-mdsol",
    author_email="glow@mdsol.com",
    description="A simple tool for processing CT.gov records",
    data_files=[("config", ["doc/schema/public.xsd"])],
)
