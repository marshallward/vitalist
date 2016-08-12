from urllib.request import urlopen
import lxml.html

vita_urls = [
    'https://en.wikipedia.org/wiki/List_of_PlayStation_Vita_games_(A%E2%80%93L)',
    'https://en.wikipedia.org/wiki/List_of_PlayStation_Vita_games_(M%E2%80%93Z)'
]

games = []

for url in vita_urls:

    res = urlopen(url)
    tree = lxml.html.parse(res)
    root = tree.getroot()
    body = root.find("body")

    topcontent = [c for c in body if c.get('id') == 'content'][0]
    content = [c for c in topcontent if c.get('id') == "bodyContent"][0]
    text = [c for c in content if c.get('id') == 'mw-content-text'][0]

    table = [c for c in text if c.get('id') == 'softwarelist'][0]
    entries = [e for e in table if e.tag == 'tr'][2:]

    for e in entries:
        td = e[0]

        if td[0].tag == 'i':
            ititle = td[0]
        elif td[0].tag == 'span' and td[1].tag == 'i':
            ititle = td[1]
        else:
            spans = [t for t in td if t.tag == 'span' and t.get('class') == 'sorttext']
            assert(spans)
            ititle = spans[0][0]

        # TODO: replace exception with explicit parsing
        try:
            title = ititle[0].text
            assert(ititle[0].tag == 'a')
        except IndexError:
            title = ititle.text

        phys = e[-2].text
        na = e[4].text
        eu = e[5].text
        jp = e[6].text

        phys_na_kw = ['US']
        phys_eu_kw = ['France', 'Germany', 'Spain', 'Europe', 'EU']

        is_phys_na = any(kw in phys for kw in phys_na_kw)
        is_phys_eu = any(kw in phys for kw in phys_eu_kw)

        is_phys = (phys == 'Yes' or is_phys_na or is_phys_eu)
        is_na = (na != 'Unreleased')
        is_eu = (eu != 'Unreleased')

        #if is_phys and (is_na or is_eu):
        if is_phys and is_eu:
            games.append(title)

with open('list.txt', 'w') as flist:
    for g in games:
        print(g, file=flist)
