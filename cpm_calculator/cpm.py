from datetime import datetime, date, timedelta
from workdays import workday

#TODO: Check for / Prevent loops
#TODO: Check - a node cannot succeed or precede itself
#TODO: Check a node by type?

class ProjectNetwork(object):
    """
    Contains a collection of Nodes i.e.
    At a minimum, contains:
         one (and only one) 'start' node
         one (and only one) 'end' node
    May contain several 'step' nodes
    """
    def __init__(self):
        self.nodes = {}
        self.latest_start = date.today()
        self.latest_finish = date.today()
        self.start_node = None
        self.finish_node = None

    def add_node(self, node):
        """
        Add a node (Node object) to the project network

        Parameters:
        node    - a node object
        """
        #if not node.get_label() in self.nodes.keys(): # prevent from adding a node twice
        self.nodes.update({node.get_label(): node})

        if node.get_node_type() == "start":
            self.start_node = node
        if node.get_node_type() == "finish":
            self.finish_node = node

        return node


    def calculate(self, driving_date=date.today(), driving_date_type="start"):
        """
        Run backwards and forward passes to calculate dates and durations.

        Parameters:
        driving date        - either the date the project is due to start, or when it must finish
                            i.e. latest start OR latest/must finish
        driving_date_type   - "start" or "finish"
        """
        self._forward_pass(self.get_start_node())
        self.get_finish_node().set_latest_finish(self.get_finish_node().get_earliest_finish())
        self._backward_pass(self.get_finish_node())


    def _forward_pass(self, node, seq=1):
        """
        Recursive routine that iterates through all node successors, beginning at the 'start' node,
        and updates the early start and early finish durations (days) for each node in the project network
        """
        # if there are no successors, then it's the last node
        node.set_earliest_finish(node.get_earliest_start() + node.get_duration())
        if node.get_sequence() == 0:
            node.set_sequence(seq)

        successors = node.get_successor_list()
        seq += 1
        for successor in successors:
            successor_node = self.get_node(successor)
            successor_node.set_sequence(seq)
            if node.get_earliest_finish() > successor_node.get_earliest_start():
                successor_node.set_earliest_start(node.get_earliest_finish())
            # successor_node.set_earliest_finish(node.get_earliest_finish() + successor_node.get_duration())
            self._forward_pass(successor_node, seq)
        

    
    def _backward_pass(self, node):
        """
        Recursive routine that iterates through all node predecessors, beginning at the 'finish' node,
        and updates the late start and late finish durations (days) for each node in the project network
        """
        node.set_latest_start(node.get_latest_finish() - node.get_duration())
        if node.get_earliest_finish() == node.get_latest_finish():
            node.set_iscritical(True)
        predecessors = node.get_predecessor_list()
        for predecessor in predecessors:
            predecessor_node = self.get_node(predecessor)
            if  predecessor_node.get_latest_finish() == 0 or predecessor_node.get_latest_finish() > node.get_latest_start():
                predecessor_node.set_latest_finish(node.get_latest_start())
            #predecessor_node.set_latest_start(predecessor_node.get_latest_finish() - predecessor_node.get_duration())
            self._backward_pass(predecessor_node)
        

    def link(self, predecessor, successor):
        """
            links two nodes and adds them to the nodes collection if they are not already there
        """
        predecessor.add_successors(successor.get_label())
        successor.add_predecessors(predecessor.get_label())
        self.add_node(predecessor)
        self.add_node(successor)

    def set_dummy_start_node(self):
        self.start_node = Node(node_type="start", label="dummy start", duration=0)
        # the add_node routine updates the start node when type is "start"
        self.start_node.set_earliest_start(0)
        self.start_node.set_earliest_finish(0)

        # get all nodes with no predecessors and add the start node as the predecessor
        for node in self.nodes.values():
            if not node.has_predecessors() and not node.get_label() == "dummy finish":
                node.add_predecessors("dummy start")
                self.start_node.add_successors(node.get_label())
        self.add_node(self.start_node)
        
    def set_dummy_finish_node(self):
        self.finish_node = Node(node_type="finish", label="dummy finish", duration=0)
        # the add_node routine updates the finish node when type is "finish"
        # get all nodes with no successors and add the finish node as the successor
        for node in self.nodes.values():
            if not node.has_successors() and not node.get_label() == "dummy start":
                node.add_successors("dummy finish")
                self.finish_node.add_predecessors(node.get_label())
        self.add_node(self.finish_node)

    def get_earliest_start_date(self, latest_finish_date, workdays=False):
        if workdays:
            return (workday(latest_finish_date,(self.get_finish_node().get_latest_finish() * -1)))
        else:
            return latest_finish_date - timedelta(self.get_finish_node().get_latest_finish())

    def update_dates_with_earliest_start(self, earliest_start_date, workdays=False):
        for node in self.get_node_list():
            if workdays:
                node.set_earliest_start_date(workday(earliest_start_date, node.get_earliest_start()))
                node.set_earliest_finish_date(workday(earliest_start_date, node.get_earliest_finish()))
                node.set_latest_start_date(workday(earliest_start_date, node.get_latest_start()))
                node.set_latest_finish_date(workday(earliest_start_date, node.get_latest_finish()))
            else:
                node.set_earliest_start_date(earliest_start_date + timedelta(node.get_earliest_start()))
                node.set_earliest_finish_date(earliest_start_date + timedelta(node.get_earliest_finish()))
                node.set_latest_start_date(earliest_start_date + timedelta(node.get_latest_start()))
                node.set_latest_finish_date(earliest_start_date + timedelta(node.get_latest_finish()))


    def update_dates_with_latest_finish(self, latest_finish_date, workdays=False):
        ealiest_start_date = self.get_earliest_start_date(latest_finish_date, workdays)
        self.update_dates_with_earliest_start(ealiest_start_date, workdays)

    def get_critical_path(self):
        nodes = [node for node in self.get_node_list() if node.is_critical()]
        nodes = sorted(nodes, key = lambda node: node.get_sequence())
        return [node.get_label() for node in nodes]

    def get_cp_duration(self):
        return self.get_finish_node().get_latest_finish()

    ### Accessors and modifiers
    def get_start_node(self):
        return self.start_node

    def get_finish_node(self):
        return self.finish_node

    def get_nodes(self):
        return self.nodes

    def get_node_list(self):
        return self.nodes.values()

    def get_node(self, label):
        return self.nodes.get(label)

    def set_start_node(self, node):
        self.start_node = node
        self.start_node.earliest_start(0) #??

    def set_finish_node(self, node):
        self.finish_node = node

class Node(object):
    def __init__(self, node_type, label, duration):

        ### properties / member variables
        self.node_type = node_type       # start, step, end
        self.label = label          # text, the activity/node label
        self.duration = duration    # int, in days 
        self.earliest_start = 0     # int
        self.earliest_finish = 0    # int
        self.latest_start = 0       # int
        self.latest_finish = 0      # int
        self.earliest_start_date = None  # date
        self.earliest_finish_date = None # date
        self.latest_start_date = None    # date
        self.latest_finish_date = None   # date
        self.dbkey = None           # any; database key, should be unique
        self.float = 0              # int, in days
        self.predecessors = set()   # set of text/labels, set preserves uniqueness
        self.successors = set()     # set of text/labels, set preserves uniqueness
        self.iscritical = False     # boolean
        self.seq = 0                # int

    def add_predecessors(self, predecessors):
        """
        Add node predecessors

        Parameters:
        predecessors    - either a string with comma-separated node label values, OR
                        a list of node label values
        """
        # print("Type - predecessors = {}".format(type(predecessors)))
        predecessor_list = []
        if isinstance(predecessors, str):
            predecessor_list = predecessors.split(",")
        if isinstance(predecessors, list):
            predecessor_list = predecessors
        self.predecessors = self.predecessors.union(predecessor_list)

    def add_successors(self, successors):
        """
        Add node successors

        Parameters:
        successors    - either a string with comma-separated node label values, OR
                        a list of node label values
        """
        # print("Type - successors = {}".format(type(successors)))
        # print("Successors = {}".format(successors))
        successor_list = []
        if isinstance(successors, str):
            successor_list = successors.split(",")
        if isinstance(successors, list):
            successor_list = successors
        self.successors = self.successors.union(successor_list)
        # print("Adding successors {} to Node {}".format(",".join(successor_list), self.get_label()))

    def has_predecessors(self):
        if len(self.predecessors) == 0:
            return False
        return True

    def has_successors(self):
        if len(self.successors) == 0:
            return False
        return True

    def is_critical(self):
        return self.iscritical

    # accessors and modifiers
    def get_node_type(self):
        return self.node_type
    
    def get_label(self):
        return self.label

    def get_duration(self):
        return self.duration

    def get_predecessor_list(self):
        return list(self.predecessors)

    def get_successor_list(self):
        return list(self.successors)

    def get_earliest_start(self):
        return self.earliest_start

    def get_earliest_finish(self):
        return self.earliest_finish

    def get_latest_start(self):
        return self.latest_start

    def get_latest_finish(self):
        return self.latest_finish

    def get_earliest_start_date(self):
        return self.earliest_start_date

    def get_earliest_finish_date(self):
        return self.earliest_finish_date

    def get_latest_start_date(self):
        return self.latest_start_date

    def get_latest_finish_date(self):
        return self.latest_finish_date

    def get_sequence(self):
        return self.seq

    def set_earliest_start(self, val):
        #TODO: validate data type
        self.earliest_start = val

    def set_earliest_finish(self, val):
        #TODO: validate data type
        self.earliest_finish = val

    def set_latest_start(self, val):
        self.latest_start = val

    def set_latest_finish(self, val):
        self.latest_finish = val

    def set_earliest_start_date(self, esd):
        #TODO: validate data type
        self.earliest_start_date = esd

    def set_earliest_finish_date(self, efd):
        #TODO: validate data type
        self.earliest_finish_date = efd

    def set_latest_start_date(self, lsd):
        self.latest_start_date = lsd

    def set_latest_finish_date(self, lfd):
        self.latest_finish_date = lfd

    def set_iscritical(self, boolean):
        if not isinstance(boolean,bool):
            return
        self.iscritical = bool

    def set_sequence(self, seq):
        self.seq = seq

    def print_dates(self):
        print("Label: {}, ESD: {}, EFD: {}, LSD: {}, LFD: {}".format(
                self.get_label(),
                self.get_earliest_start_date(),
                self.get_earliest_finish_date(),
                self.get_latest_start_date(),
                self.get_latest_finish_date()
            )
        )

    def __str__(self):
        nodestr = "Label: {}, Type: {}, Seq: {}, Duration: {}, ES: {}, EF: {}, LS: {}, LF: {}, Predecessors: {}, Successors: {}".format(
            self.get_label(), self.get_node_type(), self.get_sequence(), self.get_duration(),
            self.get_earliest_start(), self.get_earliest_finish(),
            self.get_latest_start(), self.get_latest_finish(),
            ",".join(self.get_predecessor_list()),
             ",".join(self.get_successor_list())
            )
        # return super().__str__()
        return nodestr

if __name__ == "__main__":
    nw = ProjectNetwork()

    a = nw.add_node(Node(node_type="start", label="A", duration=3))
    b = nw.add_node(Node(node_type="step", label="B", duration=4))
    c = nw.add_node(Node(node_type="step", label="C", duration=2))
    d = nw.add_node(Node(node_type="step", label="D", duration=5))
    e = nw.add_node(Node(node_type="step", label="E", duration=1))
    f = nw.add_node(Node(node_type="step", label="F", duration=2))
    g = nw.add_node(Node(node_type="step", label="G", duration=4))
    h = nw.add_node(Node(node_type="finish", label="H", duration=3))

    nw.link(a,b)
    nw.link(a,c)
    nw.link(b,d)
    nw.link(d,g)
    nw.link(g,h)
    nw.link(c,e)
    nw.link(e,g)
    nw.link(c,f)
    nw.link(f,h)

    nw.calculate()
    #print(project)
    # p.update_all()
    # print(p.get_critical_path())
    # print(p.duration)

    today = datetime.now()
    nw.update_dates_with_latest_finish(today,False)
    print("Critical Path is: {} ({} days)".format(",".join(nw.get_critical_path()), nw.get_cp_duration()))
    print("Today is {}".format(today))
    print("Earliest start - workdays = {}".format(nw.get_earliest_start_date(today, True)))
    print("Earliest start - all days = {}".format(nw.get_earliest_start_date(today, False)))

    for n in nw.get_node_list():
        n.print_dates()
        # print(n)