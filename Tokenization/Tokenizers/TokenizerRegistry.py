_tokenizer_classes = {}

def def_tokenizer_class(tokenizer_name:str, tokenizer_class):
    _tokenizer_classes[tokenizer_name] = tokenizer_class

def get_tokenizer_class(tokenizer_name:str):
    if tokenizer_name not in _tokenizer_classes:
        print("Tokenizer '%s' requested, but none was registered." % tokenizer_name)
        assert False
    return _tokenizer_classes[tokenizer_name]