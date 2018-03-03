from hitchbuild import HitchBuild
from path import Path
from pathquery import pathquery


class DirTemplate(HitchBuild):
    def __init__(self, name, src, built):
        self._name = name
        self._build_path = Path(built)
        self._src_path = Path(src)
        assert self._build_path.exists(), "{0} does not exist."
        assert self._src_path.exists(), "{0} does not exist."

    def build(self):
        for filepath in pathquery(self._src_path):
            if not filepath.isdir():
                relpath = filepath.relpath(self._src_path)
                dest_path = self._build_path.joinpath(self._name, relpath)

                if not dest_path.dirname().exists():
                    dest_path.dirname().makedirs()
                filepath.copy(dest_path)
