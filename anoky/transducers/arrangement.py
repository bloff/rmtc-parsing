from anoky.common.string_stuff import indent_string
from anoky.syntax.code import Code
from anoky.syntax.identifier import Identifier
from anoky.syntax.node import Node
from anoky.syntax.lisp_printer import lisp_printer
from anoky.common.globals import G
from anoky.transducers.read_direction import ReadDirection


class Arrangement(object):
    """
    An arrangement is defined by a list of arrangement rules (:ref:`ArrangementRule`). It traverses a single node from
    left-to-right or right-to-left. For each child of the node, for each arrangement rule, it checks if the rule is applicable,
    and, if so, applies it to transform the node at that child.
    """
    def __init__(self, rules:list, direction:ReadDirection = ReadDirection.LEFT_TO_RIGHT):
        self.rules = rules
        """A list of arrangement rules."""
        self.direction = direction
        """Whether the node should be left from left-to-right or from right-to-left."""

    # given a form h(a b c ...), parse goes through its elements
    # and for each element it checks if one of the rules in the list of ArrangementRules apply; if it does, then it is applied
    # the application of the rule returns the next element to be scanned
    # if no rule applies, the next element scanned is either the next or previous element (given by element.next and element.prev)
    # (depending on the "direction" being LEFT_TO_RIGHT or RIGHT_TO_LEFT)
    def arrange(self, node:Code):
        if not isinstance(node, Node):
            return

        element = None
        if self.direction == ReadDirection.LEFT_TO_RIGHT:
            element = node.first
        elif self.direction == ReadDirection.RIGHT_TO_LEFT:
            element = node.last

        while element is not None:
            nxt = element.next if self.direction == ReadDirection.LEFT_TO_RIGHT else element.prev

            for r in self.rules:
                if r.applies(element):

                    #region Debug Printing
                    if G.Options.PRINT_ARRANGEMENT_OUTPUTS:
                        node.insert(element, Identifier("⋅"))
                        out ="        Arrangement: " + r.name + "\n"
                        out += indent_string("BEFORE:", 12) + "\n"
                        out += indent_string(lisp_printer(node), 20)
                        print(out)
                        node.remove(element.next)
                    #endregion

                    nxt = r.apply(element)

                    # region Debug Printing
                    if G.Options.PRINT_ARRANGEMENT_OUTPUTS:
                        if nxt is None:
                            node.insert(node.last, Identifier("⋅"))
                        else:
                            node.insert(nxt, Identifier("⋅"))
                        out = indent_string("After:", 12) + "\n"
                        out += indent_string(lisp_printer(node), 20)
                        print(out)
                        if nxt is None:
                            node.remove(node.last)
                        else:
                            node.remove(nxt.next)
                    # endregion
                    break
            element = nxt

    def get_rule(self, name):
        for rule in self.rules:
            if hasattr(rule, "name") and rule.name == name:
                return rule
        return None

    def insert_rule(self, after_rule_with_name, rule):
        i = 0
        while i < len(self.rules):
            if hasattr(self.rules[i], "name") and self.rules[i].name == after_rule_with_name:
                    self.rules.insert(i + 1, rule)
                    return
            i += 1
        raise IndexError("No arrangment rule with name '%s'" % after_rule_with_name)

    def insert_rule_before(self, after_rule_with_name, rule):
        i = 0
        while i < len(self.rules):
            if hasattr(self.rules[i], "name") and self.rules[i].name == after_rule_with_name:
                self.rules.insert(i, rule)
                return
            i += 1
        raise IndexError("No arrangment rule with name '%s'" % after_rule_with_name)

# def surrounding_elements_code(element, distance_before, distance_after = 0):
#     l = []
#     e = element.prev
#     while distance_before > 0 and e is not None:
#         l.append(e.code)
#         distance_before -= 1
#     l.reverse()
#     e = element.next
#     while distance_after > 0 and e is not None:
#         l.append(e.code)
#         distance_after -= 1
#     return l if len(l) > 1 else l[0] if len(l) == 1 else None


