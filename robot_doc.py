import json
from urllib.error import HTTPError

from pyquery import PyQuery as pq
from jinja2 import Template
from docutils.core import publish_parts


"""
Script de génération de la liste des mots-clés existants dans Robot Framework
Pour fonctionner, ce script requiert les bibliothèques suivantes (à installer avec `pip install <nom>`) :

- pyquery
- jinja2
- docutils
"""


def main():
    doc_page = 'http://robotframework.org/robotframework/'
    lib_page = 'http://robotframework.org/robotframework/latest/libraries/{}.html'

    keywords = {}

    d = pq(url=doc_page)
    table = d('#standard-libraries').next().next().next()
    stdlib_names = table('tr>td:first').map(lambda i, e: e.text)
    style_tag = ''
    for lib in stdlib_names:
        try:
            print('Bibliothèque {}'.format(lib))
            lib_kw = []
            d = pq(url=lib_page.format(lib))
            raw_doc = d('head>script:last')[0].text.strip()[9:]  # skipping "libdoc = "
            raw_doc = raw_doc.replace('\\x3c', '\x3c')
            lib_doc = json.loads(raw_doc)
            for kw in lib_doc['keywords']:
                doc_parts = publish_parts(kw['shortdoc'].split('\n')[0],
                                          writer_name='html5')
                doc = doc_parts['fragment']
                style_tag = doc_parts['stylesheet']
                kw_data = {'name': kw['name'],
                           'link': lib_page.format(lib) + '#{}'.format(kw['name']),
                           'shortdoc': doc}
                lib_kw.append(kw_data)
            keywords[lib] = lib_kw
        except HTTPError as e:
            print('Erreur sur la bibliothèque {}: {}'.format(lib, e))

    with open('robot_doc.j2.html') as fd:
        tmpl = Template(fd.read())
    output = tmpl.render(keywords=keywords, style=style_tag)
    with open('robot_doc.html', 'w') as fd:
        fd.write(output)

if __name__ == '__main__':
    main()
