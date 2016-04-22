```
$ anoky --print-parse --print-macro-expanded-code
>>> rawmacro myname(element, EC):
        print "test"
        element.code[0].code.name = "pass"


——›–  Parsed source before macro expansion  –‹——
(rawmacro (myname element EC)
            (print "test")
            (= (. (. («@[]» (. element code) 0) code) name) "pass"))


——›–  Parsed source after macro expansion  –‹——
(rawmacro (myname element EC)
            (print "test")
            (= (. (. («@[]» (. element code) 0) code) name) "pass"))

>>> myname()

——›–  Parsed source before macro expansion  –‹——
(myname)

test

——›–  Parsed source after macro expansion  –‹——
(pass)


```