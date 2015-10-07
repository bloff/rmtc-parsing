EOF = -1

special_visual_width_characters = {'':2, '':2, '':2,
                                   '':2, '':2, '':2,
                                   '':2, '':2, '':2,
                                   '':2, '':2, '':2,
                                   '': 2, '': 2,
                                   '': 2, '': 2,
                                   '': 2,
                                   '': 2, '': 2,
                                   '': 2, '': 2,}

def indent_string(lines, amount=4, ch=' '):
    padding = amount * ch
    return padding + ('\n'+padding).join(lines.split('\n'))