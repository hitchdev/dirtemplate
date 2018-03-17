from hitchbuild import HitchBuild
from path import Path
from pathquery import pathquery
from strictyaml import load, MapPattern, Str, Seq, Map, Bool
from jinja2 import Template
from copy import copy
from dirtemplate.directory import Dir


class DirTemplate(HitchBuild):
    def __init__(self, name, src, dest):
        self._name = name
        self._build_path = Path(dest).abspath()
        self._src_path = Path(src).abspath()
        self._variables = {}
        self._functions = {}
        assert self._build_path.exists(), "{0} does not exist."
        assert self._src_path.exists(), "{0} does not exist."

    def with_vars(self, **variables):
        new_dirt = copy(self)
        new_dirt._variables = variables
        return new_dirt

    def with_functions(self, **functions):
        new_dirt = copy(self)
        new_dirt._functions = functions
        return new_dirt

    @property
    def _render_vars(self):
        render_vars = copy(self._variables)
        render_vars['directory'] = Dir(self._src_path)
        return render_vars

    def build(self):
        if self._src_path.joinpath("dirtemplate.yml").exists():
            config = load(
                self._src_path.joinpath("dirtemplate.yml").text(),
                Map({
                    "templated": Seq(
                        MapPattern(Str(), Map({"content": Bool()}))
                    )
                })
            ).data
        else:
            config = {"templated": []}

        src_paths = list(pathquery(self._src_path))
        remaining_src_paths = copy(src_paths)

        for template_configuration in config['templated']:
            for src_path in copy(remaining_src_paths):
                if not src_path.isdir():
                    relpath = src_path.relpath(self._src_path)
                    dest_path = self._build_path.joinpath(self._name, relpath)

                    if not dest_path.dirname().exists():
                        dest_path.dirname().makedirs()

                    if relpath in template_configuration.keys():
                        if template_configuration[relpath]['content']:
                            jinja2_template = Template(src_path.text())
                            jinja2_template.globals.update(self._functions)
                            dest_path.write_text(
                                jinja2_template.render(**self._render_vars)
                            )
                        remaining_src_paths.remove(src_path)

        for src_path in remaining_src_paths:
            relpath = src_path.relpath(self._src_path)
            dest_path = self._build_path.joinpath(self._name, relpath)

            if not dest_path.dirname().exists():
                dest_path.dirname().makedirs()
            if not src_path.isdir():
                src_path.copy(dest_path)
