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
      DirTemplate(src="src", dest="example").ensure_built()
  - Build output is:
      files:
        example/index.md: Index file
        example/insubdir/subdirectoryfile: subdirectory file
        example/fingerprint.txt: 
