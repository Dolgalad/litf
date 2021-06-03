"""
:author: Alexandre Schulz
:email: alexandre.schulz@irap.omp.eu
:brief: Creating a graph representation of the CodeModel objects in the database
"""

import networkx as nx

from apps.codes.models import CodeModel
from libs.code import status

## Node styling
class NodeStyle:
    FAILURE="color=red"
    SUCCESS="color=green"
    PENDING="color=gray"
    RUNNING="color=orange"

    REQUIREMENT="shape=box"


def add_codemodel_requirements(cm, G):
    if cm.requirements:
        for r in cm.requirements.split("\r\n"):
            if len(r):
                if not r in G:
                    G.add_node(r, style=NodeStyle.REQUIREMENT)
                # add the edge
                G.add_edge(cm.name, r)
    return G
def add_codemodel_node(cm, G):
    if not cm.name in G:
        # add node
        if cm.status==status.CodeExecutionStatus.SUCCESS:
            style=NodeStyle.SUCCESS
        elif cm.status==status.CodeExecutionStatus.PENDING:
            style=NodeStyle.PENDING
        elif cm.status==status.CodeExecutionStatus.RUNNING:
            style=NodeStyle.RUNNING
        else:
            style=NodeStyle.FAILURE
        G.add_node(cm.name, style=style)
    # add the requirements
    G=add_codemodel_requirements(cm, G)
    # add the dependencies
    for dep in cm.dependencies.all():
        G=add_codemodel_node(dep, G)
        G.add_edge(cm.name, dep.name)
    return G


def dependency_graph(user=None):
    if user:
        cm_list=CodeModel.objects.filter(author=user)
    else:
        cm_list=CodeModel.objects.all()
    # create a graph
    G=nx.DiGraph()
    for cm in cm_list:
        add_codemodel_node(cm,G)
    return G

def get_graphviz(G):
    a="""digraph G {
    rankdir=LR;
    rotation=90;
    ration="compress";
    size="10,10";
    margin=0;

""" 
    for n in G.nodes():
        a+="\t{} [{}];\n".format(n,G.nodes[n]["style"])
    for e in G.edges():
        a+="\t{} -> {};\n".format(e[0],e[1])
    a+="}"
    return a
