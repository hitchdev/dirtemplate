Templated filename and file contents:
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
            filename: yes
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      DirTemplate(src="src", dest="example")\
          .with_vars(variable="var")\
          .with_files(
              templated_md={
                  "insubdir/templated1.md": {"variable": "var1"},
                  "insubdir/templated2.md": {"variable": "var2"},
                  "insubdir/templated3.md": {},
              },
          )\
          .ensure_built()
  - Build output is:
      files:
        example/index.md: Index file
        example/insubdir/subdirectoryfile: subdirectory file
        example/insubdir/templated1.md: Templated var1 file. 
        example/insubdir/templated2.md: Templated var2 file. 
        example/insubdir/templated3.md: Templated var file. 
        example/fingerprint.txt: 
