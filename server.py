
import time
import selector

class server:

    def __init__(self, host, port = 70):
        self.host = host
        self.port = port
        self.selectors = []
        self.last_visited = 0

    def __str__(self):
        return "[server object host=%s port=%s last_visited=%s %s]" % (repr(self.host), repr(self.port), repr(self.last_visited), self.selectors)
        
    def __repr__(self):
        return self.__str__()

    def add_selector(self, s, end = 0):
        assert isinstance(s, selector.selector)
        if s.host == None:
            s.host = self.host
        if s.host != self.host:
            if s.host == None:
                s.host = self.host
                s.port = self.port
            else:
                raise AssertionError, 'selector host (%s) and server host (%s) differ' % (s.host, self.host)

        if end != 0:
            self.selectors.append(s)
        else:
            self.selectors.insert(0, s)

    def get_next_selector(self):
        if len(self.selectors) == 0:
            return None
        for i in range(len(self.selectors)):
            if self.selectors[i].last_visited == None:
                break
        return self.selectors.pop(i)

    def get_selector(self, sel):
        for x in self.selectors:
            if x.selector == sel:
                self.selectors.remove(x)
                return x
        return None

    def visited_now(self):
        self.last_visited = time.time()

    def ensure_selector(self, sel):
        x = self.get_selector(sel)
        if x == None:
            x = selector.selector(sel)
        self.add_selector(x)
        return x
