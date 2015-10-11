from Syntax.Form import Form

__author__ = 'bruno'


class PreForm(Form):
    def __init__(self, *children):
        Form.__init__(self, *children)
        self.prepend_head = None