Templated file:
  docs: templated-file
  about: |
    Copy files from one directory to another but copy jinja2.
  given:
    files:
      src/index.md: Index file
      src/templated.md: Templated {{ variable }} file.
      src/insubdir/subdirectoryfile: subdirectory file
      src/dirtemplate.yml: |
        templated:
        - templated.md:
            content: yes
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      DirTemplate(name="example", src="src", dest="built").with_vars(variable="var").ensure_built()
  - Build output is:
      files:
        built/example/index.md: Index file
        built/example/insubdir/subdirectoryfile: subdirectory file
        built/example/templated.md: Templated var file. 
