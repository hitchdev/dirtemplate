from hitchbuild import HitchBuild
from path import Path
from pathquery import pathquery
from strictyaml import load, MapPattern, Str, Seq, Map, Bool, Optional
import jinja2
from copy import copy
from dirtemplate.directory import Dir
from slugify import slugify


def render(template_text, functions, render_vars, base_templates):
    templates = base_templates if base_templates is not None else {}
    templates['template_to_render'] = template_text
    environment = jinja2.Environment(
        loader=jinja2.DictLoader(templates)
    )
    environment.globals.update(functions)
    return environment.get_template('template_to_render').render(**render_vars)


def base_templates(src_path, template_folder):
    templates = {}
    if template_folder is not None:
        for filename in src_path.joinpath(template_folder).listdir():
            relpath = filename.relpath(src_path.joinpath(template_folder))
            templates[str(relpath)] = filename.text()
    return templates


class DirTemplate(HitchBuild):
    def __init__(self, name, src, dest):
        self._name = name
        self._build_path = Path(dest).abspath()
        self._src_path = Path(src).abspath()
        self._variables = {}
        self._functions = {}
        self._files = {}
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

    def with_files(self, **files):
        new_dirt = copy(self)
        new_dirt._files = files
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
                    Optional("base templates"): Str(),
                    "templated": Seq(
                        MapPattern(Str(), Map({
                            Optional("content"): Bool(),
                            Optional("filename"): Bool(),
                        }))
                    ),
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

                    if relpath in template_configuration.keys():
                        if 'filename' in template_configuration[relpath]:
                            slug = slugify(relpath, separator=u'_')

                            if slug in self._files.keys():
                                for filename, variables in self._files[slug].items():
                                    dest_path = self._build_path.joinpath(self._name, filename)

                                    if not dest_path.dirname().exists():
                                        dest_path.dirname().makedirs()

                                    render_vars = {}

                                    for name, var in self._render_vars.items():
                                        render_vars[name] = var

                                    for name, filevar in variables.items():
                                        render_vars[name] = filevar

                                    dest_path.write_text(
                                        render(
                                            src_path.text(),
                                            self._functions,
                                            render_vars,
                                            base_templates(
                                                self._src_path,
                                                config.get("base templates")
                                            )
                                        )
                                    )                                   
                            else:
                                raise Exception((
                                    "{0} templated filename exists but not "
                                    "specified with with_files".format(relpath)
                                ))
                        else:
                            dest_path = self._build_path.joinpath(self._name, relpath)

                            if not dest_path.dirname().exists():
                                dest_path.dirname().makedirs()

                            if template_configuration[relpath]['content']:
                                dest_path.write_text(
                                    render(
                                        src_path.text(),
                                        self._functions,
                                        self._render_vars,
                                        base_templates(
                                            self._src_path,
                                            config.get("base templates")
                                        ),
                                    )
                                )

                        remaining_src_paths.remove(src_path)

        # Remember not to spit out base templates
        if "base templates" in config:
            for src_path in pathquery(self._src_path.joinpath(config['base templates'])):
                remaining_src_paths.remove(src_path)

        # Remaining non-templated files
        for src_path in remaining_src_paths:
            relpath = src_path.relpath(self._src_path)
            dest_path = self._build_path.joinpath(self._name, relpath)

            if not dest_path.dirname().exists():
                dest_path.dirname().makedirs()
            if not src_path.isdir():
                src_path.copy(dest_path)
