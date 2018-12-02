Ignore files:
  docs: ignore-files
  about: |
    Copy a bunch of files from one directory to another, ignoring
    files specified by .ignore_files(filename1, filename2, ...).
  given:
    files:
      src/index.md: Index file
      src/ignore.me: Path that should be ignoreded.
      src/ignoredir/content1: This file should be be ignored.
      src/insubdir/subdirectoryfile: subdirectory file
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      DirTemplate(name="example", src="src", dest="built")\
          .ignore_files("ignore.me", "ignoredir/content1")\
          .ensure_built()

  - Build output is:
      files:
        built/example/index.md: Index file
        built/example/insubdir/subdirectoryfile: subdirectory file
