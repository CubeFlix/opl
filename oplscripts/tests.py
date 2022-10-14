from main import *


decompiler = OPLDecompiler()

file = open('pi.opl.opc', 'rb')
file_data = file.read()
file.close()

decompiled = decompiler.decompile(file_data)

print(decompiled)