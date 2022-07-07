# useful tools for the KnowledgeBase

[KnowledgeBase by Ingo Straub](https://inforapid.org/webapp/login.php)

## knowldge.py

tool to read/modify kdb files

```bash
$ knowledge.py -h
usage: knowledge.py [-h] [-D DATABASE] [-e EXPORTDIR] [-k] [-v]
                    {categories,categorise,clean,deArrow,import,load_excel,load_opml,query,replace,sort,step_in,step_out,to_csv,args}
                    ...

tool to inspect, query and edit Knowledge Base sqlite files

positional arguments:
  {categories,categorise,clean,deArrow,import,load_excel,load_opml,query,replace,sort,step_in,step_out,to_csv,args}
                        operations
    categories          inspect the structure for categories for the templates in the KDB
    categorise          change the category from asis to tobe, empty string "" for None
    clean               remote html tags from descriptions
    deArrow             remove -> arrows from descriptions
    import              import cloud outliner cod file to a node parent
    load_excel          load an excel sheet into the KDB file
    load_opml           load OPML xml format into the KDB
    query               query a value, and filter by category
    replace             search and replace in item names
    sort                sort an items child items
    step_in             todo
    step_out            todo
    to_csv              export data to directory as tables of raw KDB types
    args                print the values for the args

optional arguments:
  -h, --help            show this help message and exit
  -D DATABASE, --database DATABASE
                        Knowledge Base database, default=Empty.kdb
  -e EXPORTDIR, --exportdir EXPORTDIR
                        output to export dir, default=export
  -k, --klobber         klobber db
  -v, --verbose         verbose logging
```

### usage

to query a kdb do the following; note the '%' for sql like patten globbing

```bash
$ pip3 install --upgrade KnowledgeBase

$ knowledge.py -D Recipies.kdb query '%' 
Recipies
Fetachini Pesto
Corn fritters
```

or you can inspect with filter parameters

```bash
$ knowledge.py query -h
usage: knowledge.py query [-h] [-d] [-u] [-a] [-r {i,o,b}] [-c CATEGORIES [CATEGORIES ...]] name

query a value, and filter by category

positional arguments:
  name                  string to search in name for

optional arguments:
  -h, --help            show this help message and exit
  -d, --description     include description
  -u, --url             include url
  -a, --attachments     include attachments
  -r {i,o,b}, --references {i,o,b}
                        include references
  -c CATEGORIES [CATEGORIES ...], --categories CATEGORIES [CATEGORIES ...]
                        restrict to categories

```


