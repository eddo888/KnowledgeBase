# useful tools for the KnowledgeBase

[KnowledgeBase by Ingo Straub](https://inforapid.org/webapp/login.php)

## knowldge.py

tool to read/modify kdb files

```bash
$ knowledge.py -h
usage: knowledge.py [-h] [-D DATABASE] [-e EXPORTDIR] [-k] [-v]
                    {clean,deArrow,export,import,inspect,load_excel,load_opml,query,replace,sort,args}
                    ...

positional arguments:
  {clean,deArrow,export,import,inspect,load_excel,load_opml,query,replace,sort,args}
                        operations
    clean
    deArrow
    export
    import
    inspect
    load_excel
    load_opml
    query
    replace
    sort
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

## outline.py

tool to read opml files and work with kdb loading formats

