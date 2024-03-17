import os
import typing
from typing import Any

from ruamel.yaml import YAML

from conda_forge_tick.migrators.core import MiniMigrator
from conda_forge_tick.os_utils import pushd

if typing.TYPE_CHECKING:
    from ..migrators_types import AttrsTypedDict


class CondaForgeYAMLCleanup(MiniMigrator):
    # if you add a key here, you need to add it to the set of
    # keys kept in the graph in make_graph.py
    keys_to_remove = [
        "min_r_ver",
        "max_r_ver",
        "min_py_ver",
        "max_py_ver",
        "compiler_stack",
    ]
    keys_to_change = [
        "test_on_native_only",
    ]

    def filter(self, attrs: "AttrsTypedDict", not_bad_str_start: str = "") -> bool:
        """only remove the keys if they are there"""
        cfy = attrs.get("conda-forge.yml", {})
        if any(k in cfy for k in self.keys_to_remove or k in self.keys_to_change):
            return False
        else:
            return True

    def migrate(self, recipe_dir: str, attrs: "AttrsTypedDict", **kwargs: Any) -> None:
        with pushd(recipe_dir):
            cfg_path = os.path.join("..", "conda-forge.yml")
            yaml = YAML()
            yaml.indent(mapping=2, sequence=4, offset=2)

            with open(cfg_path) as fp:
                cfg = yaml.load(fp.read())

            for k in self.keys_to_remove:
                if k in cfg:
                    del cfg[k]

            if "test_on_native_only" in cfg:
                value = cfg["test_on_native_only"]
                del cfg["test_on_native_only"]
                if value:
                    cfg["test"] = "native_and_emulated"

            with open(cfg_path, "w") as fp:
                yaml.dump(cfg, fp)
