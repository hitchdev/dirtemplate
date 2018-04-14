Template Error:
  docs: dir-object
  about: |
    In this example we show how a template error is flagged.
  given:
    files:
      src/index.md: |
        Index file
        ----------
        {% jinja2 tag error
      src/dirtemplate.yml: |
        templated:
        - index.md:
            content: yes
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run:
      code: |
        DirTemplate(name="example", src="src", dest="built").ensure_built()
      raises:
        type: dirtemplate.exceptions.TemplateError
        message: "Syntax error in /path/to/src/index.md on line 3:\n\nEncountered\
          \ unknown tag 'jinja2'.\n\nIndex file\n----------\n{% jinja2 tag error\n\
          \n"
