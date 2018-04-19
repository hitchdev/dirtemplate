from commandlib import run, Command, CommandError
import hitchpython
from hitchstory import StoryCollection, BaseEngine, exceptions, validate
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from hitchrun import expected
from strictyaml import Str, MapPattern, Map, Optional
from pathquery import pathquery
from commandlib import python
from hitchrun import hitch_maintenance
from hitchrun import DIR
from hitchrunpy import ExamplePythonCode, HitchRunPyException
from hitchstory import no_stacktrace_for
from templex import Templex
import hitchtest


class Engine(BaseEngine):
    """Python engine for running tests."""
    given_definition = GivenDefinition(
        files=GivenProperty(MapPattern(Str(), Str())),
        python_version=GivenProperty(Str()),
        setup=GivenProperty(Str()),
    )

    info_definition = InfoDefinition(
        docs=InfoProperty(schema=Str()),
    )

    def __init__(self, paths, settings):
        self.path = paths
        self.settings = settings

    def set_up(self):
        """Set up the environment ready to run the stories."""
        self.path.state = self.path.gen.joinpath("state")

        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        self.path.state.joinpath("built").mkdir()

        for filename, content in self.given.files.items():
            filepath = self.path.state.joinpath(filename)

            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(content)

        py_version = "3.5.0" if self.given.python_version is None else self.given.python_version
        self.python_package = hitchpython.PythonPackage(py_version)
        self.python_package.build()

        self.pip = self.python_package.cmd.pip
        self.python = self.python_package.cmd.python

        # Install debugging packages
        with hitchtest.monitor([self.path.key.joinpath("debugrequirements.txt")]) as changed:
            if changed:
                run(self.pip("install", "-r", "debugrequirements.txt").in_dir(self.path.key))

        # Uninstall and reinstall
        with hitchtest.monitor(
            pathquery(self.path.project.joinpath("dirtemplate")).ext("py")
        ) as changed:
            if changed:
                self.pip("uninstall", "dirtemplate", "-y").ignore_errors().run()
                self.pip("install", ".").in_dir(self.path.project).run()

    def _process_exception(self, string):
        return string.replace(self.path.state, "/path/to")

    @no_stacktrace_for(AssertionError)
    @no_stacktrace_for(HitchRunPyException)
    @validate(
        code=Str(),
        will_output=Str(),
        raises=Map({
            Optional("type"): Str(),
            Optional("message"): Str(),
        })
    )
    def run(self, code, will_output=None, raises=None):
        self.example_py_code = ExamplePythonCode(self.python, self.path.state)\
            .with_terminal_size(160, 100)\
            .with_setup_code(self.given.setup)
        to_run = self.example_py_code.with_code(code)

        if self.settings.get("cprofile"):
            to_run = to_run.with_cprofile(
                self.path.profile.joinpath("{0}.dat".format(self.story.slug))
            )

        result = to_run.expect_exceptions().run() if raises is not None else to_run.run()

        actual_output = result.output

        if will_output is not None:
            try:
                Templex(will_output).assert_match(actual_output)
            except AssertionError:
                if self.settings.get("overwrite artefacts"):
                    self.current_step.update(**{"will output": actual_output})
                else:
                    raise

        if raises is not None:
            exception_type = raises.get('type')
            message = raises.get('message')

            try:
                result = self.example_py_code.expect_exceptions().run()
                result.exception_was_raised(exception_type)
                exception_message = self._process_exception(result.exception.message)
                Templex(message).assert_match(exception_message)
            except AssertionError:
                if self.settings.get("overwrite artefacts"):
                    new_raises = raises.copy()
                    new_raises['message'] = exception_message
                    self.current_step.update(raises=new_raises)
                else:
                    raise

    @no_stacktrace_for(AssertionError)
    @validate(files=MapPattern(Str(), Str()))
    def build_output_is(self, files):
        for filename, content in files.items():
            filepath = self.path.state.joinpath(filename)

            assert filepath.exists(), "{0} does not exist".format(filename)
            Templex(content).assert_match(filepath.text())

        actual_files = list(pathquery(self.path.state.joinpath("built", "example")).is_not_dir())

        assert len(actual_files) == len(files.keys()), \
            "Should be:\n\n{0}\n\nAre actually:\n\n{1}\n".format(
                '\n'.join(files.keys()),
                '\n'.join(actual_files),
            )

    def on_success(self):
        self.new_story.save()


@expected(exceptions.HitchStoryException)
def rbdd(*keywords):
    """
    Run story with name containing keywords and rewrite.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"),
        Engine(
            DIR,
            {
                "overwrite artefacts": True,
                "print output": True,
            },
        )
    ).shortcut(*keywords).play()


@expected(exceptions.HitchStoryException)
def bdd(*keywords):
    """
    Run story with name containing keywords.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"),
        Engine(
            DIR,
            {
                "overwrite artefacts": False,
                "print output": True,
            },
        )
    ).shortcut(*keywords).play()


@expected(exceptions.HitchStoryException)
def regressfile(filename):
    """
    Run all stories in filename 'filename'.
    """
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {"overwrite artefacts": False})
    ).in_filename(filename).ordered_by_name().play()


@expected(exceptions.HitchStoryException)
def regression():
    """
    Continuos integration - lint and run all stories.
    """
    lint()
    StoryCollection(
        pathquery(DIR.key).ext("story"), Engine(DIR, {"overwrite artefacts": False})
    ).only_uninherited().ordered_by_name().play()


@expected(CommandError)
def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        DIR.project.joinpath("dirtemplate"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        DIR.key.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "dirtemplate"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()


def rerun(version="3.5.0"):
    """
    Rerun last example code block with specified version of python.
    """
    Command(DIR.gen.joinpath("py{0}".format(version), "bin", "python"))(
        DIR.gen.joinpath("state", "examplepythoncode.py")
    ).in_dir(DIR.gen.joinpath("state")).run()
