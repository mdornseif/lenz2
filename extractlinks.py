# --drt@un.bewaff.net
# with code from linkchecker

import re
import urlnorm
from urlparse import urljoin 

# regular expression to match an HTML tag with one given attribute
_linkMatcher = r"""
(?i)           # case insensitive
<              # open tag
\s*            # whitespace
(?P<tag>%s)    # tag name
\s+            # whitespace
([^"'>]|"[^"]*"|'[^']*')*?         #  skip leading attributes
%s             # attrib name
\s*            # whitespace
=              # equal sign
\s*            # whitespace
(?P<value>     # attribute value
 "[^"]*" |       # in double quotes
 '[^']*' |       # in single quotes
 [^\s>]+)      # unquoted
 ([^"'>]|"[^"]*"|'[^']*')*          # skip trailing attributes
>              # close tag
"""
# " <- for braindead xemacs font-lock-mode

# disable meta tag for now, the modified linkmatcher does not allow it
# (['meta'],    ['url']), # <meta http-equiv='refresh' content='x; url=...'>

# ripped mainly from HTML::Tagset.pm
LinkTags = (
(['a', 'area', 'link', 'xmp'],       ['href']),
(['blockquote', 'del', 'ins', 'q'], ['cite']),
(['form', 'isindex'],    ['action']),
(['frame', 'iframe'],  ['src', 'longdesc']),
# ignore links which are likly leading to non-textual data
#(['body', 'table', 'td', 'th', 'tr', 'ilayer'], ['background']),
#(['applet'],  ['archive', 'codebase', 'src']),
#(['bgsound'], ['src']),
#(['embed'],   ['pluginspage', 'src']),
#(['head'],    ['profile']),
#(['img'],     ['src', 'lowsrc', 'longdesc', 'usemap']),
#(['input'],   ['src', 'usemap']),
#(['layer'],   ['background', 'src']),
#(['object'],  ['classid', 'codebase', 'data', 'archive', 'usemap']),
#(['script'],  ['src', 'for'])
)

LinkPatterns = []
for tags,attrs in LinkTags:
    attr = '(%s)'%'|'.join(attrs)
    tag = '(%s)'%'|'.join(tags)
    LinkPatterns.append({'pattern': re.compile(_linkMatcher % (tag, attr),
                                               re.VERBOSE|re.DOTALL),
                         'tag': tag,
                         'attr': attr})

BasePattern = {
    'pattern': re.compile(_linkMatcher % ("base", "href"), re.VERBOSE),
    'tag': 'base',
    'attr': 'href',
    }


def get_absolute_url(urlName, baseRef, parentName):
    """search for the absolute url"""
    if urlName and ":" in urlName:
        return urlName.lower()
    elif baseRef and ":" in baseRef:
        return baseRef.lower()
    elif parentName and ":" in parentName:
        return parentName.lower()
    return ""

    
def parseForUrlsInHtml(data, location):
    # search for a possible base reference
    bases = searchInForTag(BasePattern, data)
    baseRef = None
    if len(bases)>=1:
        baseRef = bases[0][0]
        if len(bases)>1:
            print "more than one base tag found"

    # search for tags and add found tags to URL queue
    ret = {}
    for pattern in LinkPatterns:
        urls = searchInForTag(pattern, data)
        for url, name in urls:
            url = urlnorm.norms(urljoin(get_absolute_url(url, baseRef, location), url))
            ret[url] = 1
    return ret.keys()

def searchInForTag(pattern, data):
    # print "Searching for tag", `pattern['tag']`, "attribute", `pattern['attr']`
    urls = []
    index = 0
    while 1:
        match = pattern['pattern'].search(data, index)
        if not match:
            break
        index = match.end()
        # strip quotes
        url = match.group('value')
        if url[0]=='"' or url[0]=="'":
            url = url[1:]
        if url[-1]=='"' or url[-1]=="'":
            url = url[:-1]
        urls.append((url, match.group('tag')))
    return urls


if __name__ == '__main__':
    print parseForUrlsInHtml(open("example.html").read(), 'http://md.hudora.de/bizarr/')
