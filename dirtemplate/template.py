from hitchbuild import HitchBuild
from path import Path
from pathquery import pathquery
from strictyaml import load, MapPattern, Str, Map, Bool
from jinja2 import Template
from copy import copy


class DirTemplate(HitchBuild):
    def __init__(self, name, src, built):
        self._name = name
        self._build_path = Path(built).abspath()
        self._src_path = Path(src).abspath()
        self._variables = {}
        assert self._build_path.exists(), "{0} does not exist."
        assert self._src_path.exists(), "{0} does not exist."

    def with_vars(self, **variables):
        new_dirt = copy(self)
        new_dirt._variables = variables
        return new_dirt

    def build(self):
        if self._src_path.joinpath("dirtemplate.yml").exists():
            config = load(
                self._src_path.joinpath("dirtemplate.yml").text(),
                MapPattern(Str(), Map({"jinja2": Bool()}))
            ).data
        else:
            config = {}

        for src_path in pathquery(self._src_path):
            if not src_path.isdir():
                relpath = src_path.relpath(self._src_path)
                dest_path = self._build_path.joinpath(self._name, relpath)

                if not dest_path.dirname().exists():
                    dest_path.dirname().makedirs()

                if relpath in config.keys():
                    if config[relpath]['jinja2']:
                        dest_path.write_text(
                            Template(src_path.text()).render(**self._variables)
                        )
                else:
                    src_path.copy(dest_path)
