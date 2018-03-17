Table of contents:
  docs: dir-object
  about: |
    In this example a templated index file is created using
    jinja2 that points to other files in the dirtemplate.
  given:
    files:
      src/index.md: |
        Index file
        ----------
        {% for dirfile in directory.location("subdir") %}
        * [{{ title(dirfile) }}](subdir/{{ dirfile.namebase }})
        {%- endfor %}
      src/subdir/page1.md: |
        Page 1 title
        ============
        
        Page 1 contents        
      src/subdir/page2.md: |
        Page 2 title
        ============
        
        Page 2 contents
      src/dirtemplate.yml: |
        templated:
        - index.md:
            content: yes
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      def title(dirfile):
          return dirfile.text().split("=")[0].rstrip("\n")

      DirTemplate(name="example", src="src", dest="built").with_functions(title=title).ensure_built()
  - Build output is:
      files:
        built/example/index.md: |-
          Index file
          ----------
          
          * [Page 1 title](subdir/page1)
          * [Page 2 title](subdir/page2)
        built/example/subdir/page1.md: |
          Page 1 title
          ============
          
          Page 1 contents        
        built/example/subdir/page2.md: |-
          Page 2 title
          ============
          
          Page 2 contents
