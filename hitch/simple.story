Simple:
  docs: simple
  about: |
    Copy a bunch of files from one directory to another.
  given:
    files:
      src/index.md: Index file
      src/insubdir/subdirectoryfile: subdirectory file
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      DirTemplate(name="example", src="src", dest="built").ensure_built()
  - Build output is:
      files:
        built/example/index.md: Index file
        built/example/insubdir/subdirectoryfile: subdirectory file
