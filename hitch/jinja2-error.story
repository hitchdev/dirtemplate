Template Error:
  docs: dir-object
  about: |
    In this example we show how a template error is flagged.
  given:
    setup: |
      from dirtemplate import DirTemplate
  variations:
    Syntax error:
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
      steps:
      - Run:
          code: |
            DirTemplate(src="src", dest="example").ensure_built()
          raises:
            type: dirtemplate.exceptions.TemplateLineError
            message: "Syntax error in /path/to/src/index.md on line 3:\n\nEncountered\
              \ unknown tag 'jinja2'.\n\nIndex file\n----------\n{% jinja2 tag error\n\
              \n"

              
    Undefined error:
      given:
        files:
          src/index.md: |
            Index file
            ----------
            {% if undefined.value %}
            do thing
            {% endif %}
          src/dirtemplate.yml: |
            templated:
            - index.md:
                content: yes
      steps:
      - Run:
          code: |
            DirTemplate(src="src", dest="example").ensure_built()
          raises:
            type: dirtemplate.exceptions.TemplateError
            message: "Undefined var in /path/to/src/index.md: 'undefined' is undefined"
