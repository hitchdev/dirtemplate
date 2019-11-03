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
        
        Subdir:
        
        {% for dirfile in (subdir("subdir").ext("md") - subdir("subdir").named("index.md"))|sort() %}
        * [{{ title(dirfile) }}](subdir/{{ dirfile.namebase }})
        {%- endfor %}
      src/subdir/index.md: |
        Index
        =====
        
        {% for dirfile in (thisdir.ext("md") - thisdir.named("index.md"))|sort() %}
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
        - subdir/index.md:
            content: yes
        - index.md:
            content: yes
    setup: |
      from dirtemplate import DirTemplate
  steps:
  - Run: |
      def title(dirfile):
          return dirfile.text().split("=")[0].rstrip("\n")

      DirTemplate(src="src", dest="example")\
          .with_files(
              contentpage_md={
                  "subdir/page1.md": {"title": "Page 1"},
                  "subdir/page2.md": {"title": "Page 2"},
              }
          )\
          .with_functions(title=title).ensure_built()
  - Build output is:
      files:
        example/fingerprint.txt:
        example/subdir/index.md: |-
          Index
          =====

          
          * [Page 1 title](subdir/page1)
          * [Page 2 title](subdir/page2)
          * [Page 3 title](subdir/page3)
        example/subdir/page1.md: |-
          Page 1 title
          ============
          
          Page 1 contents
        example/subdir/page2.md: |-
          Page 2 title
          ============
          
          Page 2 contents
        example/subdir/page3.md: |-
          Page 3 title
          ============
          
          Page 3 contents
        example/index.md: |-
          Index file
          ----------
          
          Subdir:
          
          
          * [Page 1 title](subdir/page1)
          * [Page 2 title](subdir/page2)
          * [Page 3 title](subdir/page3)
