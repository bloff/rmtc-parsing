from rmtc.Common.Globals import G

G.Options.PRINT_ERRORS_ON_CREATION = True
G.Options.PRINT_TOKENS = False
G.Options.PRINT_TREE_TRANSDUCER_OUTPUTS = False
G.Options.PRINT_TREE_TRANSDUCER_OUTPUTS_LIST = ['Primary', 'Block']
G.Options.PRINT_ARRANGEMENT_OUTPUTS = False # True


import struct
G.Options.INT_LENGTH = struct.calcsize("P")
G.Options.MAX_INT = (1<<G.Options.INT_LENGTH*8 - 1) - 1
G.Options.MAX_UINT = (1<<G.Options.INT_LENGTH*8) - 1
G.Options.POINTER_LENGTH = struct.calcsize("P")
G.Options.MAX_TYPE_DEPTH = G.Options.MAX_INT


