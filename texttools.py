# --drt@un.bewaff.net - http://c0re.jp/

def splitlines(data):
    """Split date into seperate lines regardles of line end.

    Can handle '\\n', '\\r', '\\n\\r' and '\\r\\n' als line-end indicator
    """

    data = data.replace('\r\n', '\n').replace('\n\r', '\n').replace('\r','\n')
    return data.split('\n')
