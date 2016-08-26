from collections import defaultdict
from urllib.request import urlopen
import lxml.html

vita_urls = [
    'https://en.wikipedia.org/wiki/List_of_PlayStation_Vita_games_(A%E2%80%93L)',
    'https://en.wikipedia.org/wiki/List_of_PlayStation_Vita_games_(M%E2%80%93Z)'
]

phys_kw = {}
phys_kw['na'] = ['US']
phys_kw['fr'] = ['France']
phys_kw['de'] = ['Germany']
phys_kw['es'] = ['Spain']
phys_kw['eu'] = phys_kw['fr'] + phys_kw['de'] + phys_kw['es'] + ['Europe', 'EU']
phys_kw['jp'] = ['Japan', 'JP']
# TODO: SEA
# TODO: South Korea

games = []
reg_games = defaultdict(list)

for url in vita_urls:

    res = urlopen(url)
    tree = lxml.html.parse(res)
    root = tree.getroot()
    body = root.find('body')

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

        phys_data = e[-2].text

        dates = {}
        dates['na'] = e[4].text
        dates['eu'] = e[5].text
        dates['jp'] = e[6].text

        # check for region-exclusive release
        is_reg_excl = {}
        for reg in ('na', 'eu', 'jp'):
            # Probably a more clever way to do this
            other_regs = (r for r in ('na', 'eu', 'jp') if r != reg)

            is_excl_date = (dates[reg] not in ('Unreleased', 'TBA') and
                            not any(dates[r] not in ('Unreleased', 'TBA')
                                    for r in other_regs))

            is_reg_excl[reg] = is_excl_date

        # Check for physical release
        is_phys = {}
        is_phys_excl = {}
        for reg in ('na', 'eu', 'jp'):
            is_phys_excl_kw = any(kw in phys_data for kw in phys_kw[reg])

            is_phys[reg] = ((phys_data == 'Yes' or is_phys_excl_kw)
                            and dates[reg] not in ('Unreleased', 'TBA'))

            is_phys_excl[reg] = (is_phys_excl_kw or
                                 (is_phys[reg] and is_reg_excl[reg]))

        for reg in ('na', 'eu', 'jp'):
            if is_phys_excl[reg]:
                reg_games[reg].append(title)

        if any(is_phys[reg] for reg in ('na', 'eu', 'jp')):
            games.append(title)

# Output

# All physicals
with open('physcarts.txt', 'w') as flist:
    for g in games:
        print(g, file=flist)

# Region-exclusive physicals (need SK, Asia)
for reg in ('na', 'eu', 'jp'):
    fname = 'phys_{}_excl.txt'.format(reg)
    with open(fname, 'w') as flist:
        for gname in reg_games[reg]:
            print(gname, file=flist)
