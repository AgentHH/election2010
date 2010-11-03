#!/usr/bin/env python
import urllib2, sys, time, BeautifulSoup, pickle, re, heapq, datetime
from operator import itemgetter

propnames = {
    "19": "Legalize Marijuana in CA, Regulate and Tax",
    "20": "Redistricting of Congressional Districts",
    "21": "State Park Funding. Vehicle License Surcharge.",
    "22": "Prohibit State From Taking Some Local Funds",
    "23": "Suspend Air Pollution Control Law (AB 32)",
    "24": "Repeal Allowance of Lower Business Tax Liability",
    "25": "Simple Majority Vote to Pass Budget",
    "26": "2/3 Vote for Some State/Local Fees",
    "27": "Eliminate State Redistricting Commission",
}

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

pickler = pickle.Pickler(open("results.txt", "a"))

def get_number(s):
    return long(s.replace(",", ""))

while 1:
    try:
        f = None
        while f == None:
            try:
                f = urllib2.urlopen("http://vote.sos.ca.gov/returns/all-state/")
            except:
                sys.stdout.write("Failed to get page[0F")
                time.sleep(5)
                pass
        #f = open("example.html")
        #f = open("values.html")
        stuff = f.read()
        dom = BeautifulSoup.BeautifulSoup(stuff)

        reporting = dom.find("div", "Reporting").contents
        print "\n".join((reporting[0], reporting[2]))

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
                print "%s:" % (title)
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
                    #print "    %s%s[0m has %d votes" % (parties[party][1], name, votes)
                    c[name] = (votes, party)
                totalvotes = sum([x[0] for x in c.values()])
                if not totalvotes:
                    print "    NO RESULTS"
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
                    print "    %s%3d.%d % 8d %s[0m" % (parties[p][1], perint, perdec, v, n)
                if restvotes:
                    per = float(restvotes) / totalvotes * 100
                    perint = int(per % 100)
                    perdec = int((per * 10) % 10)
                    print "    %3d.%d % 8d (all others)" % (perint, perdec, restvotes)
            else:
                print "%s:" % (title)
                for prop in props:
                    nametag = prop.find("td", "propName")
                    bold = nametag.find("b")
                    if bold:
                        name = bold.contents[0]
                        name = ''.join((name, ": ", propnames[name]))
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
                        print "    %s %3d.%d  +%8d  %s[0m" % (c, perint, perdec, diff, name)
                    else:
                        print "    NO RESULTS          %s" % (name)
    except:
#        print("error")
        raise

    time.sleep(5 * 60)

