from pathquery import pathquery


class Dir(object):
    def __init__(self, build_path):
        self._build_path = build_path

    def location(self, subdirectory):
        return pathquery(self._build_path.joinpath(subdirectory)).is_not_dir()
