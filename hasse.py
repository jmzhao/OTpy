import pydot
import erc

def hasse(t, skb) :
    g = pydot.Dot(graph_type='digraph')
    for i in t.get_constraint_indices() :
        g.add_node(pydot.Node(i, label=t.get_constraint(index=i).abbr))
    for e in skb :
        if e.cnt_value(erc.vW) == 1 :
            wi = tuple(e.get_indices(erc.vW))[0]
            for li in e.get_indices(erc.vL) :
                g.add_edge(pydot.Edge(wi, li))
        else :
            ll = tuple(e.get_indices(erc.vL))
            for wi in e.get_indices(erc.vW) :
                for li in ll :
                    g.add_edge(pydot.Edge(wi, li, label='or', style='dashed'))
    return g