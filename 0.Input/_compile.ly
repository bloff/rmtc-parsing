a b, c:
  d e

a b, c
  d e, f
  head: arg


head a0 b0
     a, b
     c

b, c # needs fixing

a + b
    c d

function (a, b, c) => #(function a b c)

make-form-out-of-seq-macro (a, b, c) => #(a b c)

written code -rmtc-> Code -macro-expansion-> Code -code-generation-> Python AST -python-compiler-> bytecode ...

function (elm1, elm2
          subcall: arg1, arg2)
         ...

function [elm1, elm2, subcall(arg1, arg2)], ...

#(function (@[] elm1 elm2 (subcall arg1 arg2)) ...)


head   i1, i1
       i3
   ...

#
    => BEGIN a b , c INDENT BEGIN d e , f END BEGIN ... END END

    => BEGIN a b , c  X  d e , f   X  ... X END


    import
    from ... import

    compile_time_import ...

    (compile_time_import my_macros)


    (my_macro_1 a b c)

