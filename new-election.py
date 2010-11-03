#!/usr/bin/env python
import urllib2, sys, time, BeautifulSoup, re, heapq, datetime
from operator import itemgetter

parties = {
    "Non":      ["Non-affiliated",        "[30;47m"],
    "Lib":      ["Libertarian",           "[30;43m"],
    "AI":       ["American Independent",  "[30;46m"],
    "Rep":      ["Republican",            "[37;41m"],
    "P&amp;F":  ["Peace and Freedom",     "[30;45m"],
    "Dem":      ["Democrat",              "[37;44m"],
    "Grn":      ["Green",                 "[30;42m"],
}

partyre = re.compile(r"(?P<name>.+) \((?P<party>[^)]+)\)$")

def get_number(s):
    return long(s.replace(",", ""))

sys.stdout.write("[H[J")
sys.stdout.flush()
while 1:
    try:
        f = None
        page = 0
        while f == None:
            try:
                f = urllib2.urlopen("http://vote.sos.ca.gov/returns/all-state/")
            except:
                page = page + 1
                sys.stdout.write("Failed to get page (%d) [1G" % (page))
                sys.stdout.flush()
                time.sleep(5)
                pass
        #f = open("example.html")
        #f = open("values.html")
        stuff = f.read()
        dom = BeautifulSoup.BeautifulSoup(stuff)

        reporting = dom.find("div", "Reporting").contents
        ts = [reporting[0], reporting[2]]

        cs = []
        ps = []

        for race in dom.findAll("div", "party-map-div"):
            (title,) = race.find("a").contents
            results = race.findNextSibling("table", "content")
            candidates = results.findAll("tr", "candRow")
            props = results.findAll("tr", {"class": ["PropRow1", "PropRow2"]})
            if len(candidates) and len(props):
                print "mixed candidates and props for %s, uh oh" % (title)
                continue
            if len(candidates) == 0 and len(props) == 0:
                print "no candidates or props for %s, uh oh" % (title)
            if len(candidates):
                cs += ["%s:" % (title)]
                c = {}
                for candidate in candidates:
                    garbage = candidate.find("td", "candName").contents[0]
                    m = partyre.match(garbage)
                    if not m:
                        print "match failed for \"%s\"" % (name)
                        continue
                    name = m.group("name")
                    party = m.group("party")

                    votes = get_number(candidate.find("td", "candVotes").contents[0])
                    c[name] = (votes, party)
                totalvotes = sum([x[0] for x in c.values()])
                if not totalvotes:
                    cs += ["    NO RESULTS"]
                    continue
                stuff = heapq.nlargest(2, c.iteritems(), itemgetter(1))
                restvotes = totalvotes - sum([x[1][0] for x in stuff])
                for dude in stuff:
                    p = dude[1][1]
                    n = dude[0]
                    v = dude[1][0]
                    per = float(v) / totalvotes * 100
                    perint = int(per % 100)
                    perdec = int((per * 10) % 10)
                    cs += ["    %s%3d.%d % 8d %s[0m" % (parties[p][1], perint, perdec, v, n)]
                if restvotes:
                    per = float(restvotes) / totalvotes * 100
                    perint = int(per % 100)
                    perdec = int((per * 10) % 10)
                    cs += ["    %3d.%d % 8d (all others)" % (perint, perdec, restvotes)]
            else:
                ps += ["%s:" % (title)]
                for prop in props:
                    nametag = prop.find("td", "propName")
                    bold = nametag.find("b")
                    if bold:
                        name = bold.contents[0]
                        name = ''.join((name, ": ", nametag.contents[1].strip()))
                    else:
                        name = nametag.contents[0]
                    yes = get_number(prop.find("td", "propYTot").contents[0])
                    no = get_number(prop.find("td", "propNTot").contents[0])
                    if yes + no:
                        if yes > no:
                            a = yes
                            b = no
                            c = "[30;42mY"
                        elif no > yes:
                            a = no
                            b = yes
                            c = "[37;41mN"
                        else:
                            a = yes
                            b = no
                            c = "[30;43mT"
                        per = float(a) / (a + b) * 100
                        perint = int(per % 100)
                        perdec = int((per * 10) % 10)
                        diff = a - b
                        ps += ["    %s %3d.%d  +%8d  %s[0m" % (c, perint, perdec, diff, name)]
                    else:
                        ps += ["    NO RESULTS          %s" % (name)]

        sys.stdout.write("[H[J")
        for line in ts:
            sys.stdout.write("".join(("[40G", line, "\n")))
        sys.stdout.write("[5E")
        for line in ps:
            sys.stdout.write("".join(("[40G", line, "\n")))
        sys.stdout.write("[H")
        for line in cs:
            sys.stdout.write("".join((line, "\n")))
        sys.stdout.flush()
        #print ts
        #print cs
        #print ps
    except:
#        print("error")
        raise

    time.sleep(5 * 60)

