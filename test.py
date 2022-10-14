from opl.opl import OPLCompiler, OPLExecutor, OPECompiler, OPEExecutor

code = '''120
0
  2 s"MyModule.lib" i0
  118 i0
  200 s"Hello World!
"
  30 i1 i1
  84
  121
  0
  2 s"MyModule.lib" i0
  118 i0
  200 s"Hello World!
"
  30 i1 i1
  1 i0'''

c = OPLCompiler()
ccode = c.compile(code)

# e = OPLExecutor()
# e.execute(ccode)

o = OPECompiler()
maincode = ccode
f = open('MyModule.lib', 'rb')
files = {'MyModule.lib' : f.read()}
f.close()
ope = o.compile(maincode, files)

e = OPEExecutor()
print(e.execute(ope))

from opl.opl.functions import split_code, remove_leading_spaces
print(remove_leading_spaces(split_code('''0 1 0
123 gds vcd

	fdjskl " gds
fdawg" 2
fdjsk f
   fdsjk''')))