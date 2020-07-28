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

### usage

to inspect a kdb do the following;

```bash
$ pip3 install KnowledgeBase

$ knowledge.py -D Recipies.kdb inspect 
Recipies
Fetachini Pesto
Corn fritters
```

or you can inspect with filter parameters

```bash
$ knowledge.py -D Recipies.kdb inspect -h
usage: knowledge.py inspect [-h] [-n NAME] [-r] [-c] [-a]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  the name of the element
  -r, --references      list references
  -c, --categories      list categories
  -a, --attachments     list attachments
```

which would give you filtered results like this

```bash
$ knowledge.py -D Recipies.kdb inspect -n 'Recipies' -r
Recipies
	Fetachini Pesto
	Corn fritters

```

## outline.py

tool to read opml files and work with kdb loading formats

