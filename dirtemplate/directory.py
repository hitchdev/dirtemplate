from pathquery import pathquery


class Dir(object):
    def __init__(self, src_path):
        self._src_path = src_path

    def location(self, subdirectory):
        return pathquery(self._src_path.joinpath(subdirectory)).is_not_dir()
