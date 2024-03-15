import warnings
from pathlib import Path

import pytest
from pydantic import ValidationError

from conda_forge_tick.models.node_attributes import NodeAttributes

"""
These tests validate that the node attributes files in the node_attrs directory are valid JSON and
conform to the NodeAttributes schema.

Since we currently do not use the NodeAttributes schema in production, and also do not enforce some rules
in the conda-smithy linter (e.g. valid URLs in , it is very possible that failures in these tests can occur.

The most likely cause of these failures is that the meta.yaml file of an upstream feedstock does not conform to
the MetaYaml schema - note that some fields of the NodeAttributes schema are derived directly from the meta.yaml file.

You can add the name of a feedstock to the KNOWN_BAD_FEEDSTOCKS list if you know that it will fail these tests.
After fixing the issue, you can remove the feedstock from the list.
"""

NODE_ATTRS_DIR = Path("node_attrs")

KNOWN_BAD_FEEDSTOCKS = {
    "gmatelastoplasticqpot3d",  # missing platforms
    "tqdm",  # invalid conda-forge.yaml build platform "win:azure"
    "semi-ate-stdf",  # missing platforms
    "thrust",  # missing platforms
    "make_arq",  # invalid conda-forge.yml build platform "windows"
    "cub",  # missing platforms
    "mamba",  # outdated version field in dependency graph (package.version field removed in meta.yaml)
    "napari",  # outdated version field in dependency graph (package.version field removed in meta.yaml)
    "birka",  # outdated version field in dependency graph (package.version field removed in meta.yaml)
    "xsimd",  # recipe/meta.yaml about.doc_url has a typo in the URL scheme
    "pytao",  # recipe/meta.yaml about.dev_url has a typo in the URL scheme
    "anyqt",  # recipe/meta.yaml about.dev_url has a typo in the URL scheme
    "cubed",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "condastats",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "pytermgui",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "torcpy",  # recipe/meta.yaml about.dev_url has typo
    "scikit-plot",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "matbench-genmetrics",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "neutronics_material_maker",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "gulp",  # recipe/meta.yaml about.dev_url has invalid URL scheme
    "wagtail-bakery",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "mp_time_split",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "shippinglabel",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "cddlib",  # recipe/meta.yaml about.doc_url has "ftp" URL scheme (and is unreachable)
    "cf-autotick-bot-test-package",  # recipe/meta.yaml source.sha256 is invalid
    "vs2008_runtime",  # node attributes error: build.skip is true for non-Windows, but osx and linux are platforms
    "everett",  # recipe/meta.yaml about.dev_url has invalid URL scheme
    "scheil",  # recipe/meta.yaml about.doc_url is not a valid URL
    "llspy-slm",  # recipe/meta.yaml about.doc_url has invalid URL scheme
    "path.py",  # build.noarch: true in meta.yaml, which should probably be build.noarch: python
    "parallel-hashmap",  # build.noarch: true (should be generic) but also probably broken on Windows
    "airflow",  # "grayskull-update" should be "update-grayskull" in conda-forge.yml
    "ipython_memory_usage",  # bot.inspect should be bot.inspection in conda-forge.yml
    "rich-argparse",  # grayskull-update should be update-grayskull in conda-forge.yml
    "htbuilder",  # bot.inspect should be bot.inspection in conda-forge.yml
    "cdsdashboards",  # invalid value for bot.inspection: false (conda-forge.yml)
    "stats_arrays",  # "grayskull-update" should be "update-grayskull" in conda-forge.yml
    "spyder",  # invalid value for bot.inspection: false (conda-forge.yml)
    "textual-fastdatatable",  # bot.inspect should be bot.inspection in conda-forge.yml
    "aiohttp",  # bot.inspect should be bot.inspection in conda-forge.yml
    "buildbot",  # bot.inspect should be bot.inspection in conda-forge.yml
    "sqlalchemy-drill",  # "grayskull-update" should be "update-grayskull" in conda-forge.yml
    "sphinx-sitemap",  # typo in bot.inspection (conda-forge.yml)
    "alibabacloud-openapi-util",  # "grayskull-update" should be "update-grayskull" in conda-forge.yml
    "st-annotated-text",  # bot.inspect should be bot.inspection in conda-forge.yml
    "dustgoggles",  # invalid value for bot.inspection: false (conda-forge.yml)
    "cx_freeze",  # invalid value for bot.inspection: false (conda-forge.yml)
    "buildbot-www",  # bot.inspect should be bot.inspection in conda-forge.yml
    "wgpu-native",  # bot.abi_migration_branches should be string, not float (conda-forge.yml)
    "google-ads",  # "grayskull-update" should be "update-grayskull" in conda-forge.yml
    "dnspython",  # "grayskull-update" should be "update-grayskull" in conda-forge.yml
    "pyobjc-framework-corebluetooth",  # bot.inspect should be bot.inspection in conda-forge.yml
    "azure-storage-queue",  # bot.inspect should be bot.inspection in conda-forge.yml
    "semi-ate-testers",  # invalid value for bot.inspection: false (conda-forge.yml)
    "sisl",  # bot.inspection is false (conda-forge.yml)
    "unicorn-binance-suite",  # bot.inspection is false (conda-forge.yml)
    "sepal-ui",  # bot.inspection is false (conda-forge.yml)
    "apsg",  # bot.inspection is false (conda-forge.yml)
    "intake_pattern_catalog",  # bot.inspection is false (conda-forge.yml)
    "pymc-marketing",  # typo in bot.inspection (conda-forge.yml)
    "requests-cache",  # bot.inspection is false (conda-forge.yml)
    "graphite2",  # provider.win has invalid value "win".
    "lbapcommon",  # provider.osx_arm64 has invalid value "osx_64". See issue #64 of the feedstock.
    "root",  # provider.osx_arm64 has invalid value "osx_64". See issue #238 of the feedstock.
    "vector-classes",  # provider.osx_arm64 has invalid value "osx_64". See issue #9 of the feedstock.
    "espaloma",  # typo in `conda-forge.yml`.azure
    "sparc-x",  # `conda-forge.yml`.channels is unexpected
    "jupyter_core",  # `conda-forge.yml`.abi_migration_branches is unexpected, should be moved to `conda-forge.yml`.bot
    "rerun-sdk",  # unrecognized field `conda-forge.yml`.azure.artifact_retention_days
    "bamnostic",  # unrecognized field `conda-forge.yml`.build
    "r-v8",  # unrecognized field `conda-forge.yml`.github.win
    "python-utils",  # unrecognized field `conda-forge.yml`.dependencies
    "pyrosm",  # unrecognized option `conda-forge.yml`.build, legacy field `conda-forge.yml`.matrix does not validate
    "sketchnu",  # `conda-forge.yml`.conda_build.pkg_format may not be None
    "fd-find",  # invalid `conda-forge.yml`.test_on_native_only value
    "micromamba",  # invalid value for `conda-forge.yml`.channel_priority
    "conda-build",  # unrecognized field `conda-forge.yml`.remote-ci-setup - use _ instead of -!
    "sense2vec",  # `conda-forge.yml`.channels is unexpected
    "mpi4py",  # legacy field `conda-forge.yml`.matrix needs further investigation
    "rpaframework",  # `conda-forge.yml`.channel_priority has invalid value "False"
    # see https://github.com/conda-forge/conda-smithy/issues/1863 for the top-level build platform fields
    "nbgrader",  # `conda-forge.yml`.linux_ppc64le should be removed (see above)
    "sccache",  # `conda-forge.yml`.linux_aarch64 should be removed (see above)
    "cmdstan",  # `conda-forge.yml`.linux_aarch64 and linux_ppc64le should be removed (see above)
    "uarray",  # `conda-forge.yml`.linux_ppc64le and linux_aarch64 should be removed (see above)
    "sourmash-minimal",  # `conda-forge.yml`.linux_ppc64le and linux_aarch64 should be removed (see above)
    "libtk",  # `conda-forge.yml`.linux_ppc64le and linux_aarch64 should be removed (see above)
    "libsimpleitk",  # `conda-forge.yml`.linux_ppc64le and linux_aarch64 should be removed (see above)
    "stackvana-afw",  # `conda-forge.yml`.remote_ci_setup must be list
}


def pytest_generate_tests(metafunc):
    files = list(NODE_ATTRS_DIR.rglob("*.json"))
    valid_files = [f for f in files if f.stem not in KNOWN_BAD_FEEDSTOCKS]
    invalid_files = [f for f in files if f.stem in KNOWN_BAD_FEEDSTOCKS]

    if not files:
        raise ValueError(
            "No node attributes files found. Make sure the cf-graph is in the current working directory."
        )

    nonexistent_bad_feedstocks = [
        feedstock
        for feedstock in KNOWN_BAD_FEEDSTOCKS
        if feedstock not in (f.stem for f in files)
    ]
    if nonexistent_bad_feedstocks:
        warnings.warn(
            f"Some feedstocks from the KNOWN_BAD_FEEDSTOCKS do not exist: {nonexistent_bad_feedstocks}"
        )

    if "node_file_valid" in metafunc.fixturenames:
        metafunc.parametrize("node_file_valid", valid_files, ids=lambda x: x.stem)

    if "node_file_invalid" in metafunc.fixturenames:
        metafunc.parametrize("node_file_invalid", invalid_files, ids=lambda x: x.stem)


def test_validate_node_attrs_valid(node_file_valid):
    with open(node_file_valid) as f:
        node_attrs = f.read()
    NodeAttributes.validate_json(node_attrs)


def test_validate_node_attrs_invalid(node_file_invalid):
    with open(node_file_invalid) as f:
        node_attrs = f.read()
    with pytest.raises(ValidationError):
        NodeAttributes.validate_json(node_attrs)
