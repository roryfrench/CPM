from datetime import date

#TODO: Check for / Prevent loops
#TODO: Check - a node cannot succeed or precede itself

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
        if not node.get_label() in self.nodes.keys(): # prevent from adding a node twice
            self.nodes.update({node.get_label(): node})


    def calculate(self, driving_date=date.today(), driving_date_type="start"):
        """
        Run backwards and forward passes to calculate dates and durations.

        Parameters:
        driving date        - either the date the project is due to start, or when it must finish
                            i.e. latest start OR latest/must finish
        driving_date_type   - "start" or "finish"
        """
        fp = {} # forward pass nodes with no successors
        self._forward_pass(self.get_start_node(), fp)
        self.get_finish_node().set_latest_finish(self.get_finish_node().get_earliest_finish())
        self._backward_pass(self.get_finish_node())

        # if driving_date_type == "finish":
        #     self.latest_finish = driving_date
        #     self._backward_pass(self.get_finish_node())
        #     self._forward_pass(self.get_start_node())
        # else:
        #     self.latest_start = driving_date
        #     self._forward_pass(self.get_start_node())
        #     self._backward_pass(self.get_finish_node)
 

    def _forward_pass(self, node, fp):
        """
        Recursive routine that iterates through all node successors, beginning at the 'start' node,
        and updates the early start and early finish durations (days) for each node in the project network
        """
        # if there are no successors, then it's the last node
        successors = node.get_successor_list()
        if len(successors) == 0:
            fp.update({node.get_earliest_finish: node.get_label()})

        for successor in successors:
            successor_node = self.get_step_node(successor)
            successor_node.set_earliest_start(node.get_earliest_finish())
            successor_node.set_earliest_finish(node.get_earliest_finish() + successor_node.get_duration())
            self._forward_pass(successor_node, fp)

    
    def _backward_pass(self, node):
        """
        Recursive routine that iterates through all node predecessors, beginning at the 'finish' node,
        and updates the late start and late finish durations (days) for each node in the project network
        """
        predecessors = node.get_predecessor_list()
        if len(predecessors) == 0:
            pass

        for predecessor in predecessors:
            predecessor_node = self.get_step_node(predecessor)
            predecessor_node.set_latest_finish(node.get_latest_start())
            predecessor_node.set_latest_start(node.get_latest_start() - predecessor_node.get_duration())
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
        self.start_node = Node(type="start", label="start", duration=0)
        self.start_node.set_earliest_start(0)
        self.start_node.set_earliest_finish(0)

        # get all nodes with no predecessors and add the start node as the predecessor
        for node in self.nodes.values():
            if not node.has_predecessors():
                node.add_predecessors("start")
        
    def set_dummy_finish_node(self):
        self.finish_node = Node(type="finish", label="finish", duration=0)

        # get all nodes with no successors and add the finish node as the successor
        for node in self.nodes.values():
            if not node.has_successors():
                node.add_successors("finish")

    ### Accessors and modifiers
    def get_start_node(self):
        return self.start_node

    def get_finish_node(self):
        return self.finish_node

    def get_step_nodes(self):
        return self.nodes

    def get_step_node(self, label):
        return self.nodes.get(label)

    def set_start_node(self, node):
        self.start_node = node
        self.start_node.earliest_start_date(0) #??

    def set_finish_node(self, node):
        self.finish_node = node

class Node(object):
    def __init__(self, type, label, duration):

        ### properties / member variables
        self.node_type = None       # start, step, end
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

    def add_predecessors(self, predecessors):
        """
        Add node predecessors

        Parameters:
        predecessors    - either a string with comma-separated node label values, OR
                        a list of node label values
        """
        if type(predecessors) == 'str':
            predecessor_list = predecessors.split(",")
        if type(predecessors) == 'list':
            predecessor_list = predecessors
        self.predecessors = self.predecessors.union(predecessor_list)

    def add_successors(self, successors):
        """
        Add node successors

        Parameters:
        successors    - either a string with comma-separated node label values, OR
                        a list of node label values
        """
        if type(successors) == 'str':
            successor_list = successors.split(",")
        if type(successors) == 'list':
            successor_list = successors
        self.successors = self.successors.union(successor_list)

    def has_predecessors(self):
        if len(self.predecessors) == 0:
            return False
        return True

    def has_successors(self):
        if len(self.successors) == 0:
            return False
        return True

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

    def set_earliest_start(self, val):
        #TODO: validate data type
        self.earliest_start = val

    def set_earliest_finish(self, val):
        #TODO: validate data type
        self.earliest_finish = val

    def set_latest_finish(self, val):
        self.latest_finish = val