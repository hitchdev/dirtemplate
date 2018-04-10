Base Templates Folder:
  docs: dir-object
  about: |
    If you need to use:
    
    * extends
    * include
    
    To either inherit from a base template or embed a snippet
    in a page template, then you can create a base templates
    folder and use that in other templates.
  given:
    files:
      src/index.md: |
        {% extends "base.md" %}
        {% block contents %}
        
        Content1
        
        {% include "content2.md" %}
        
        {% endblock %}
      src/base/base.md: |
        Title
        =====
        {% block contents %}
        
        {% endblock contents %}
      src/base/content2.md: |
        Content2
      src/dirtemplate.yml: |
        base templates: base
        templated:
        - index.md:
            content: yes
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      DirTemplate(name="example", src="src", dest="built").ensure_built()
  - Build output is:
      files:
        built/example/index.md: |
          Title
          =====
          
          
          Content1
          
          Content2
          
          
