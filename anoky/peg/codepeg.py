from typing import Union, List

from anoky.common.string_stuff import indent_string
from anoky.common.util import is_not_none
from Parser.BlackroseParser import BlackflagParser
# from Semantics.Analysis import SemanticAnalysisContext
# from Semantics.Code.Util import is_symbol
# from Semantics.Coercion.CoerceToNumeric import numeric_type_coerces
# from Semantics.Domain import name_to_domain, ExpressionDomain
# from Semantics.Types.Bootstrap0 import Type, Int
# from Semantics.Types.Inheritance import class_inherits
from anoky.common.errors import SemanticAnalysisError
from anoky.common.record import Record
from anoky.syntax.code import Code
from anoky.syntax.form import Form
from anoky.syntax.identifier import Identifier
from anoky.syntax.lisp_printer import lisp_printer, succinct_lisp_printer
from anoky.syntax.node import Node as SyntaxNode, Element
from anoky.syntax.seq import Seq
from anoky.syntax.util import is_identifier, is_form, is_seq


class Matcher(object):

    def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
        """

        :param element: The element to be matched.
        :param memo: The memoizing dict for the current parse.
        :param context: A context variable, to allow matchers used at different compilation stages to access the appropraite context for that stage.
        :param justify_failure: Whether, in case of failure, a string should be constructed explaining why the rule failed to match.
        :return: Either False, None --- if rule failed to match and justify_failure is False --- or
        False, string_explaining_why_rule_failed_to_match --- if rule failed to match and justify_failure is true --- or True, Element, if the rule matched;
            then element is the element to be matched by subsequent matchers (could be None).
        """
        raise NotImplementedError()

class Condition(object):
    def check(self, element:Element, context, justify_failure:bool=False) -> (bool, Union[Element,str]):
        """
        Returns a pair `(holds, element)`, where `holds` says whether the condition holds true,
          and `element` is either the given element, or an expansion of the given element
          (some conditions may change the element, e.g., by doing semantic analysis).
        """
        raise NotImplementedError();

class ParseTree(dict):
    """
    A node in a parse-tree. It specifies a sequence of elements matched by the parse, the name of the rule
    that matched these elements, and the children of the node are the parse-trees for the subrules that were used
    in the matching.
    """
    def __init__(self, _name:str = None, _element:Element=None, _next_element:Element=None):
        super(ParseTree, self).__init__()
        self.__dict__ = self
        self._name = _name
        """The name of the node."""
        self._element = _element
        """The element containing the first element in the code matched by the parse."""
        self._next_element = _next_element
        """The element immediately following the last element matched by the parse."""
        self._finalized = False
        """If finalized is set to True, accessing an undefined attribute of an instance of a
        ParseTree will return None, instead of raising AttributeError."""

    def __getattr__(self, item):
        if self._finalized:
            return self.__dict__.get(item, None)
        elif item not in self.__dict__:
            raise AttributeError()
        else:
            return self.__dict__[item]

    def finalize(self):
        self._finalized = True
        for key, item in self.items():
            if isinstance(item, ParseTree):
                item.finalize()
            elif isinstance(item, list) and len(item) > 0 and isinstance(item[0], ParseTree):
                for e in item:
                    e.finalize()

    def __call__(self) -> Element:
        """Calling a parse-tree returns the first element matched by it."""
        return self._element

    def __str__(self):
        my_code = "`%s`" % succinct_lisp_printer(self())
        for key, value in self.__dict__.items():
            if key[0] != "_":
                if isinstance(value, list):
                    lst = ""
                    for i, itm in enumerate(value):
                        lst += "\n(%d) %s" %(i, str(value[0]))
                    lst = indent_string(lst)
                    my_code += "\n" + indent_string(key + "[%s]:%s" % (len(value),lst))
                else:
                    my_code += "\n" + indent_string(key + ": " + str(value))
        return my_code

class Rule(object):
    """
    A rule is a possibly named matcher, together with certain condititons.

    A rule matches a given element if the matcher does, and all the conditions apply.

    The outcome of checking whether a rule applies is memoized, so that each rule only tests a given element once.

    The parsing of the rule also builds the parse-tree.
    """
    def __init__(self, matcher:Matcher=None, name:str=None, code:str=None):
        self.matcher = matcher
        self.name = name
        self.code = code
        self.conditions = []


    def match(self, element:Element, memo:dict, context=None, force_list:bool = False, justify_failure:bool = False) -> (bool, Union[Element, str]):
        """
        Checks whether the rule applies.
        :param element: The element to be tested.
        :param memo: The memoizing dictionary. Also stores the parse-tree of the invoking parent rule
             If justify_failure=True, also stores and a map from elements to the rules that were used to match those elements.
        :param A: A semantic analysis context (some conditions are semantic). May be `None` if no conditions are semantic.
        :param force_list: Whether a single successful match of this rule should appear as a list in the parse-tree.
        :param justify_failure: Whether, on failure, a string should be produced explaining why the rule failed to match.
        :return: A pair `(rule_applies, next_element_to_be_scanned_in_form)`.
        """

        if justify_failure:
            if id(element) not in memo:
                memo[id(element)] = {self}
            elif self not in memo[id(element)]:
                memo[id(element)].add(self)



        key = (id(self), id(element))

        # Anonymous rules are not added to the parse tree, nor do they have any conditions associated with them.
        if self.name is None:
            # First we check if this rule was already tested on the given element
            if key in memo:
                # if so, we return the previous outcome
                return memo[key]
            else:
                # otherwise, we check if the matcher matches, and if so we remember the outcome
                # value should be a pair `matching, next_element`
                matching, ret = self.matcher.match(element, memo, context, justify_failure)
                if not matching and justify_failure:
                    if self.code is not None:
                        justification = "In rule '%s':\n" % self.code
                        justification += indent_string(ret)
                        ret = justification
                memo[key] = matching, ret
                return matching, ret

        # But named rules *are* added to the parse tree, and they *can* have conditions associated with them
        else:
            def _update_parent(parent, name, node):
                """
                At the time a rule is found to apply, the node in the parse-tree corresponding to the parent rule is updated.
                  An attribute is defined at the parent node, whose name is the name of the current rule, and whose value
                  is:
                    * If the current rule matched a single time as a child of the parent rule, then this attribute is the single parse-tree node of the current rule.
                    * If the current rule matched multiple times, or force_list is True, then this attribute is a list containing parse-tree nodes for every
                      successful matching of the current rule as a child of the parent rule.
                :param parent: The node of the parent rule in the parse tree.
                :param name: The name of the current rule.
                :param node: The node matched by the current rule.
                """
                if parent is not None:
                    # If the current rule has already matched as a child of the parent rule
                    if hasattr(parent, name):
                        current = parent[name]
                        # we make the parent's <current-rule's name> attribute to be a list to which we append
                        # the current rule's parse-tree node
                        if isinstance(current, ParseTree):
                            parent[name] = [current, node]
                        else:
                            assert isinstance(current, list)
                            current.append(node)
                    else:
                        if force_list:
                            parent[name] = [node]
                        else:
                            parent[name] = node


            assert isinstance(self.name, str)
            # parent holds the parent rule invoking the current rule, if any
            parent = memo['#parent'] if '#parent' in memo else None

            # If we already tested this rule on the given element, we return the result
            if key in memo:
                matching, next_element, tree_node = memo[key]
                if matching and parent is not None:
                    _update_parent(parent, self.name, tree_node)
                if not matching and justify_failure:
                    justification = tree_node
            else:
                # Otherwise
                # we create a new parse-tree node for the current rule
                tree_node = ParseTree()
                # we set the current rule as the invoking parent rule
                memo['#parent'] = tree_node
                # we test whether the rule's matcher matches the given element
                justification = None
                next_element = None

                matching, ret = self.matcher.match(element, memo, context, justify_failure)

                # If matching failed and a justification for failure has been requested, store it in the "justification" variable
                if justify_failure and not matching:
                    justification = "In rule '%s <- %s':\n" % (self.name, self.code)
                    justification += indent_string(ret)
                else:
                    next_element = ret

                if matching:
                    # if matching succeeded, we check if every condition associated with the current rule applies
                    for condition in self.conditions:
                        condition_passed, ret = condition.check(element, context, justify_failure)

                        # Again we store a justification for failure in case the condition failed to pass
                        if justify_failure and not condition_passed:
                            justification = "In rule '%s <- %s':\n" % (self.name, self.code)
                            justification += indent_string(ret)
                        else:
                            element = ret

                        # A failure of any condition will result in the rule failing to apply
                        if not condition_passed:
                            matching = False
                            break

                if matching:
                    # If the matcher matches and all conditions apply, then we have
                    # successfully applied the current rule at the given element,
                    # so we construct the parse-tree node for this rule
                    tree_node._name = self.name
                    tree_node._element = element
                    tree_node._next_element = next_element
                    # we memoize the outcome
                    memo[key] = matching, next_element, tree_node
                    # and we update the parent node in the parse-tree
                    _update_parent(parent, self.name, tree_node)
                else:
                    # if the matcher does not apply, we remember that, and associate
                    # a justification for having failed (if none was requested, justification will
                    # equal None).
                    memo[key] = matching, next_element, justification

                if parent is not None: memo['#parent'] = parent

            if matching:
                return matching, next_element
            else:
                return False, (justification if justify_failure else None)

    def add_condition(self, condition:Condition):
        self.conditions.append(condition)

_tmp = 0

class Matchers:
    class ByReference(Matcher):
        def __init__(self, rule):
            self.rule = rule

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            return self.rule.match(element, memo, context, justify_failure=justify_failure)

    class Sequence(Matcher):
        def __init__(self, rules):
            self.rules = rules

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            next_element = element
            for rule in self.rules:
                matching, next_element = rule.match(next_element, memo, context, justify_failure=justify_failure)
                if not matching: return False, next_element

            return True, next_element

    class Or(Matcher):
        def __init__(self, rules):
            self.rules = rules

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            if justify_failure:
                justification = ""
            else:
                justification = None

            # The subrules which we will try to match may possibly update the parent
            # ParseTree node with key/value pairs; but we only wish to retain those
            # key/value pairs set by the subrule which actually matches (if any);
            # So what we do is create a placeholder parent, and if we found a rule that matches
            # we then copy the keys in that placeholder to the real parent
            parent = memo['#parent']
            placeholder_parent = Record()
            memo['#parent'] = placeholder_parent
            for rule in self.rules:
                matching, next_element = rule.match(element, memo, context, justify_failure=justify_failure)
                if matching:
                    if parent is not None:
                        parent.__dict__.update(placeholder_parent)
                    memo['#parent'] = parent
                    return True, next_element
                else:
                    placeholder_parent.clear()
                    if justify_failure:
                        justification += next_element
                        justification += '\n'

            memo['#parent'] = parent
            return False, justification

    class And(Matcher):
        def __init__(self, inner_rules: List[Rule]):
            self.inner_rules = inner_rules

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            first_next_element = None
            for rule in self.inner_rules:
                matching, next_element = rule.match(element, memo, context, justify_failure=justify_failure)
                if not matching: return False, next_element
                if first_next_element is None: first_next_element = next_element
            return True, first_next_element

    class Not(Matcher):
        def __init__(self, inner_rule: Rule):
            self.inner_rule = inner_rule

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            matching, next_element = self.inner_rule.match(element, memo, context, justify_failure=justify_failure)
            if not matching: return True, element.next
            return False, ("%s: Inner rule matched the input '%s'." % (str(element.code.range), str(element.code)) if justify_failure else None)

    class Optional(Matcher):
        def __init__(self, inner_rule:Rule):
            self.inner_rule = inner_rule

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            matching, next_element = self.inner_rule.match(element, memo, context, justify_failure=justify_failure)
            if matching: return True, next_element
            else: return True, element

    class MatchIdentifier(Matcher):
        def __init__(self, identifier:Identifier):
            self.name = identifier.full_name

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            if is_identifier(element, self.name): # or is_symbol(element, self.name):
                return True, element.next
            else:
                if justify_failure:
                    if is_identifier(element): # or is_symbol(element):
                        return False, "Expected symbol or identifier called '%s', found '%s'." % (self.name, str(lisp_printer(element)))
                    elif is_not_none(element, ".code.range"):
                        return False, "%s: Given element '%s' was not an identifier or symbol." % (str(element.code.range), str(lisp_printer(element)))
                    else:
                        return False, "No element was given."
                else:
                    return False, None

    class MatchAnyOnething(Matcher):
        def __init__(self):
            pass

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            if element is not None:
                return True, element.next
            else:
                return False, ("%s: Expected another element, found none." % str(element.code.range) if justify_failure else None)

    class MatchAnything(Matcher):
        def __init__(self):
            pass

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            return True, None


    class Node(Matcher):
        def __init__(self, rules:list, NodeType):
            self.rules = rules
            self.NodeType = NodeType
            assert issubclass(NodeType, SyntaxNode)

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            if element is None: return False, None
            node = element.code

            if not isinstance(node, self.NodeType):
                if justify_failure:
                    justification = "%s: Expected a node of type '%s'" % (str(element.code.range), str(self.NodeType.__name__))
                    justification += "." if not isinstance(node, SyntaxNode) else ", but found node of type '%s' instead." % node.__class__.__name__
                    return False, justification
                else:
                    return False, None

            next_element = node.first
            global _tmp
            _tmp += 1
            for rule in self.rules:
                matching, next_element = rule.match(next_element, memo, context, justify_failure=justify_failure)
                if not matching:
                    return False, next_element

            if next_element is not None: # fail if we didn't match the entire form
                if not justify_failure:
                    return False, None

                justification = "%s: Unmatched element '%s'.\n" % (str(next_element.code.range), str(next_element.code))
                if id(next_element) in memo:
                    justification += "The following rules attempted to match said element but failed:\n"
                    rules = memo[id(next_element)]
                    for rule in rules:
                        # if rule in self.rules:
                            matching, j = rule.match(next_element, memo, context, justify_failure=True)
                            if not matching:
                                justification += indent_string(j) + "\n"
                return False, justification


            return True, element.next

    class ZeroOrMore(Matcher):
        def __init__(self, inner_rule:Rule):
            self.inner_rule = inner_rule

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            next_element = element
            while next_element is not None:
                matching, try_next = self.inner_rule.match(next_element, memo, context, force_list=True, justify_failure=justify_failure)
                if matching: next_element = try_next
                else: break
            return True, next_element

    class OneOrMore(Matcher):
        def __init__(self, inner_rule:Rule):
            self.inner_rule = inner_rule

        def match(self, element:Element, memo:dict, context, justify_failure:bool=False) -> (bool, Union[Element, str]):
            matching, try_next = self.inner_rule.match(element, memo, context, force_list=True, justify_failure=justify_failure)
            if not matching: return False, try_next
            next_element = element.next
            while next_element is not None:
                matching, try_next = self.inner_rule.match(next_element, memo, context, force_list=True, justify_failure=justify_failure)
                if matching: next_element = try_next
                else: break
            return True, next_element


class Conditions:
    class Identifier(Condition):
        def check(self, element:Element, context, justify_failure:bool=False) -> (bool, Union[Element,str]):
            b = is_identifier(element)
            if not b and justify_failure:
                return False, "Element '%s' is not an identifier." % lisp_printer(element)
            else:
                return b, element

    # class Analyse(Condition):
    #     def __init__(self, domain = None):
    #         if domain is not None:
    #             self.domain = name_to_domain(domain)
    #         else:
    #             self.domain = None
    #
    #
    #     def check(self, element:Element, context, justify_failure:bool=False) -> (bool, Union[Element,str]):
    #         if self.domain is None:
    #             context.analyse(element)
    #             return True, element
    #         else:
    #             with context.let(domain=self.domain):
    #                 context.analyse(element)
    #                 return True, element

    # class CompileTimeValue(Condition):
    #     def __init__(self, type_code: Code):
    #         self.type_code = type_code
    #         self.analysed_type_code = None
    #
    #     def check(self, element:Element, context, justify_failure:bool=False) -> (bool, Union[Element,str]):
    #         context.analyse(element)
    #
    #         if self.analysed_type_code is None: # bootstrap compiler hack; actually this analysis should be done
    #                                              #  when the rule is defined, not when it's first used
    #             with context.let(domain=ExpressionDomain):
    #                 self.analysed_type_code = Element(self.type_code)
    #                 context.analyse(self.analysed_type_code)
    #
    #         b = (class_inherits(self.analysed_type_code.type, Type) and
    #                 self.analysed_type_code.computed_value is not None and
    #                 class_inherits(element.type, self.analysed_type_code.computed_value) and
    #                 element.computed_value is not None)
    #
    #         if not b and justify_failure:
    #             if not class_inherits(self.analysed_type_code.type, Type):
    #                 return False, "%s: Code is not a type." % str(self.analysed_type_code.code.range)
    #             elif self.analysed_type_code.computed_value is None:
    #                 return False, "%s: Failed to compute value at compile-time." % str(self.analysed_type_code.code.range)
    #             elif not class_inherits(element.type, self.analysed_type_code.computed_value):
    #                 return False, "%s: Code is not of type '%s'." % (str(element.code.range), lisp_printer(element))
    #             else:
    #                 assert element.computed_value is None
    #                 return False, "%s: Failed to compute value at compile-time." % str(element.code.range)
    #         else:
    #             return b, element

    # class IntLiteral(Condition):
    #     def __init__(self):
    #         pass
    #
    #     def check(self, element:Element, context, justify_failure:bool=False) -> (bool, Union[Element,str]):
    #         context.analyse(element)
    #
    #         b = (numeric_type_coerces(element.type, Int) and
    #                 element.computed_value is not None)
    #
    #         if not b and justify_failure:
    #             if not numeric_type_coerces(element.type, Int):
    #                 return False, "%s: Code is not of integer type." % str(element.code.range)
    #             else:
    #                 assert element.computed_value is None
    #                 return False, "%s: Failed to compute value at compile-time." % str(element.code.range)
    #         else:
    #             return b, element

    # class Type(Condition):
    #     def __init__(self, type_code: Code):
    #         self.type_code = type_code
    #         self.analysed_type_code = None
    #
    #     def check(self, element:Element, context, justify_failure:bool=False) -> (bool, Union[Element,str]):
    #         context.analyse(element)
    #         if self.analysed_type_code is None: # bootstrap compiler hack; actually this analysis should be done
    #                                              #  when the rule is defined, not when it's first used
    #             with context.let(domain=ExpressionDomain):
    #                 self.analysed_type_code = Element(self.type_code)
    #                 context.analyse(self.analysed_type_code)
    #
    #         b = (class_inherits(self.analysed_type_code.type, Type) and
    #                 self.analysed_type_code.computed_value is not None and
    #                 class_inherits(element.type, self.analysed_type_code.computed_value))
    #
    #         if not b and justify_failure:
    #             if not class_inherits(self.analysed_type_code.type, Type):
    #                 return False, \
    #                        "Code specifying type to be inherited in the type-inherits rule (`%s`) is not a type." % \
    #                        lisp_printer(self.analysed_type_code)
    #             elif self.analysed_type_code.computed_value is None:
    #                 return False, \
    #                        "Cannot determine compile-time value of code specifying type to be inherited " \
    #                        "in the type-inherits rule (`%s`)." % lisp_printer(self.analysed_type_code)
    #             else:
    #                 assert not class_inherits(element.type, self.analysed_type_code.computed_value)
    #                 return False, "%s: Code is not of type %s" % \
    #                        (str(element.code.range), lisp_printer(self.analysed_type_code))
    #         else:
    #             return b, element



class Parser(object):
    _lyc_parser = BlackflagParser()

    def __init__(self, code:str):
        code_node = Parser._lyc_parser.parse(code)
        self.peg_rules = {}
        self.start_rule = None
        self.code = code

        for elm in code_node:
            form = elm.code
            assert is_form(form)
            head = form.first
            if is_identifier(head, '<-'):
                # extract rule_name
                assert is_identifier(form[1])
                rule_name = form[1].code.name

                # compile the rule into a parser
                assert len(form) == 3 # Todo: add rule checks
                rule_spec = form[2].code


                rule = self._compile_rule(rule_spec, rule_name=rule_name)

                if self.start_rule is None: self.start_rule = rule

            else:
                if is_form(elm.code):
                    self._compile_condition(elm.code)
                else:
                    raise SemanticAnalysisError(elm.code.range, "Unable to parse PEG rule '%s'." % str(elm.code))

        for rule_name, rule in self.peg_rules.items():
            if rule.matcher is None:
                rule.matcher = Matchers.MatchAnyOnething()

    def parse(self, element, context):
        memo = {}
        matching, next_element = self.start_rule.match(element, memo, context)
        if matching:
            parse_tree = memo['#parent']
            parse_tree.finalize()
            return True, parse_tree
        else:
            matching, justification = self.start_rule.match(element, {}, context, justify_failure=True)
            return False, justification



    def _compile_rule(self, rule_spec, rule_name=None) -> Rule:
        if is_identifier(rule_spec):
            if is_identifier(rule_spec, "^..."):
                matcher = Matchers.MatchAnything()
            else:
                matcher = Matchers.MatchIdentifier(rule_spec)
        elif is_form(rule_spec):
            # Recursive call to rule
            if is_identifier(rule_spec.first, "$"):
                assert len(rule_spec) == 2
                assert is_identifier(rule_spec[1])
                referenced_rule_name = rule_spec[1].code.name
                referenced_rule = self._get_rule(referenced_rule_name)
                if rule_name is None or rule_name == referenced_rule_name:
                    return referenced_rule
                else:
                    matcher = Matchers.ByReference(referenced_rule)
            # zero or more
            elif is_identifier(rule_spec.first, "^*"):
                inner_rule = self._get_inner_rule(rule_spec)
                matcher = Matchers.ZeroOrMore(inner_rule)
            # one or more
            elif is_identifier(rule_spec.first, "^+"):
                inner_rule = self._get_inner_rule(rule_spec)
                matcher = Matchers.OneOrMore(inner_rule)
            # optional
            elif is_identifier(rule_spec.first, "^?"):
                inner_rule = self._get_inner_rule(rule_spec)
                matcher = Matchers.Optional(inner_rule)
            # conjunction of rules
            elif is_identifier(rule_spec.first, "^&"): # FIXME to be N-ary
                inner_rules = [self._compile_rule(inner_rule_spec.code) for inner_rule_spec in rule_spec.iterate_from(1)]
                matcher = Matchers.And(inner_rules)
            # disjunction of rules
            elif is_identifier(rule_spec.first, "^|"):
                inner_rules = [self._compile_rule(inner_rule_spec.code) for inner_rule_spec in rule_spec.iterate_from(1)]
                matcher = Matchers.Or(inner_rules)
            # negation
            elif is_identifier(rule_spec.first, "^!"):
                inner_rule = self._get_inner_rule(rule_spec)
                matcher = Matchers.Not(inner_rule)
            # escape character
            elif is_identifier(rule_spec.first, "\\"):
                assert len(rule_spec) == 2
                assert is_identifier(rule_spec[1])
                matcher = Matchers.MatchIdentifier(rule_spec[1].code.name)
            else:
                inner_rules = [self._compile_rule(inner_rule_spec.code) for inner_rule_spec in rule_spec.iterate_from(0)]
                matcher = Matchers.Node(inner_rules, Form)
        elif is_seq(rule_spec):
            inner_rules = [self._compile_rule(inner_rule_spec.code) for inner_rule_spec in rule_spec.iterate_from(0)]
            matcher = Matchers.Node(inner_rules, Seq)
        else:
            assert False

        current_rule_code_str = self.code[rule_spec.range.first_position.index:rule_spec.range.position_after.index]

        if rule_name is not None:
            rule = self._get_rule(rule_name)
            if rule.matcher is None:
                rule.matcher = matcher
                rule.code = current_rule_code_str
            else:
                old_matcher = rule.matcher
                new_matcher_rule = Rule(matcher, code=current_rule_code_str)
                if isinstance(old_matcher, Matchers.Or):
                    old_matcher.rules.append(new_matcher_rule)
                else:
                    old_matcher_rule = Rule(old_matcher, code=rule.code)
                    rule.matcher = Matchers.Or([old_matcher_rule, new_matcher_rule])
                rule.code = "... <%d cases> ..." % len(rule.matcher.rules)
        else:
            rule = Rule(matcher)
            rule.code = current_rule_code_str




        return rule

    def _get_inner_rule(self, rule_spec:Form) -> Rule:
        assert len(rule_spec) >= 2
        if len(rule_spec) == 2:
            return self._compile_rule(rule_spec[1].code)
        else:
            subrules = [self._compile_rule(subrule.code) for subrule in rule_spec.iterate_from(1)]
            return Rule(Matchers.Sequence(subrules))

    def _get_rule(self, rule_name, code:str=None) -> Rule:
        if rule_name in self.peg_rules:
            return self.peg_rules[rule_name]
        else:
            rule = Rule(name=rule_name)
            self.peg_rules[rule_name] = rule
            return rule

    def _compile_condition(self, condition:Form):
        head = condition.first.code
        if is_identifier(head, "identifier"):
            if len(condition) != 2 or not is_identifier(condition[1]):
                raise SemanticAnalysisError(condition[1].code.range, "Failed to parse PEG condition, '%s', expected 'identifier <rule-name-identifier>, <type>'." % condition.code)
            rule_name = condition[1].code.name
            peg_rule = self._get_rule(rule_name)
            peg_rule.add_condition(Conditions.Identifier())

        elif is_identifier(head, "analyse") or is_identifier(head, "analyze"):
            arg = condition[1].code
            if is_form(arg):
                if len(condition) != 2 or len(arg) != 3 or not is_identifier(arg[0], "as") or not is_identifier(arg[1]) or not is_identifier(arg[2]):
                    raise SemanticAnalysisError(arg.code.range, "Failed to parse PEG condition, '%s', expected 'analyse <rule-name-identifier> as <dispatch-context-identifier>'." % arg.code)
                rule_name = arg[1].code.name
                domain = arg[2].code.name
            else:
                if len(condition) != 2 or not is_identifier(arg):
                    raise SemanticAnalysisError(arg.code.range, "Failed to parse PEG condition, '%s', expected 'analyse <rule-name-identifier>'." % arg.code)
                rule_name = arg.code.name
                domain = None
            peg_rule = self._get_rule(rule_name)
            peg_rule.add_condition(Conditions.Analyse(domain))
        elif is_identifier(head, "compile-time-value"):
            if len(condition) != 3 or not is_identifier(condition[1]):
                raise SemanticAnalysisError(condition[1].code.range, "Failed to parse PEG condition, '%s', expected 'compile-time-value <rule-name-identifier>, <type>'." % condition.code)
            rule_name = condition[1].code.name
            peg_rule = self._get_rule(rule_name)
            peg_rule.add_condition(Conditions.CompileTimeValue(condition[2].code))
        elif is_identifier(head, "≤ₜ") or is_identifier(head, "type-inherits"):
            if len(condition) != 3 or not is_identifier(condition[1]):
                raise SemanticAnalysisError(condition[1].code.range, "Failed to parse PEG condition, '%s', expected '<rule-name-identifier> ≤ₜ <type>'." % condition.code)
            rule_name = condition[1].code.name
            peg_rule = self._get_rule(rule_name)
            peg_rule.add_condition(Conditions.Type(condition[2].code))
        else:
            raise SemanticAnalysisError(condition.range, "Failed to parse PEG rule `%s`" % succinct_lisp_printer(condition))



# if __name__ == "__main__":
#     parser = Parser("^!⦅elif ⦆  ^!⦅else ⦆")
#     form = Form(Identifier("a"))
#     print( parser.parse())