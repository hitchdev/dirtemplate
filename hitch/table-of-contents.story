Table of contents:
  docs: dir-object
  about: |
    In this example a templated index file is created using
    jinja2 that points to other generated files in the
    dirtemplate.
    
    Note the order of files listed in dirtemplate.yml - 
    contentpage.md comes first.
  given:
    files:
      src/index.md: |
        Index file
        ----------
        {% for dirfile in directory.location("subdir") %}
        * [{{ title(dirfile) }}](subdir/{{ dirfile.namebase }})
        {%- endfor %}
      src/subdir/page3.md: |
        Page 3 title
        ============
        
        Page 3 contents
      src/contentpage.md: |
        {{ title }} title
        ============
        
        {{ title }} contents
      src/dirtemplate.yml: |
        templated:
        - contentpage.md:
            content: yes
            filename: yes
        - index.md:
            content: yes
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      def title(dirfile):
          return dirfile.text().split("=")[0].rstrip("\n")

      DirTemplate(name="example", src="src", dest="built")\
          .with_files(
              contentpage_md={
                  "subdir/page1.md": {"title": "Page 1"},
                  "subdir/page2.md": {"title": "Page 2"},
              }
          )\
          .with_functions(title=title).ensure_built()
  - Build output is:
      files:
        built/example/subdir/page1.md: |-
          Page 1 title
          ============
          
          Page 1 contents
        built/example/subdir/page2.md: |-
          Page 2 title
          ============
          
          Page 2 contents
        built/example/subdir/page3.md: |-
          Page 3 title
          ============
          
          Page 3 contents
        built/example/index.md: |-
          Index file
          ----------
          
          * [Page 1 title](subdir/page1)
          * [Page 2 title](subdir/page2)
          * [Page 3 title](subdir/page3)
