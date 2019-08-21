import cpm
from datetime import datetime

a = {
    "label": "A",
    "duration": 3,
    "successors": "B,C"
}
b = {
    "label": "B",
    "duration": 4,
    "successors": "D"
}
c = {
    "label": "C",
    "duration": 2,
    "successors": "E,F"
}
d = {
    "label": "D",
    "duration": 5,
    "successors": "G"
}
e = {
    "label": "E",
    "duration": 1,
    "successors": "G"
}
f = {
    "label": "F",
    "duration": 2,
    "successors": "H"
}
g = {
    "label": "G",
    "duration": 4,
    "successors": "H"
}
h = {
    "label": "H",
    "duration": 3,
    "successors": None
}
network = cpm.ProjectNetwork()
state_steps = [a,b,c,d,e,f,g,h]
for step in state_steps:
    node = cpm.Node(node_type="step", label=step.get("label"), duration=step.get("duration"))
    successor_list = []
    if step.get("successors"):
        successor_list.extend([s for s in state_steps if s.get("label") in step.get("successors").split(",")])
    for successor in successor_list:
        successor_node = cpm.Node(node_type="step", label=successor.get("label"), duration=successor.get("duration"))
        network.link(node, successor_node)
# attach dummy start and finish nodes - these methods will automatically link nodes in the cpm model
# without predecessors or successors to the dummy start and dummy finish nodes (respectively)
network.set_dummy_start_node()
network.set_dummy_finish_node()
### calculate the cpm metrics / days
network.calculate()
### get the critical activity date and calculate the cpm date metrics
network.update_dates_with_latest_finish(datetime.today())
print("Activity Earliest Start {} - {}".format(type(datetime.today()), datetime.today()))
print("Critical Path is: {} ({} days)".format(",".join(network.get_critical_path()), network.get_cp_duration()))
print("Earliest start - workdays = {}".format(network.get_earliest_start_date(datetime.today(), True)))
print("Earliest start - all days = {}".format(network.get_earliest_start_date(datetime.today(), False)))

for n in network.get_node_list():
        print(n)