import lzma, marshal

f = open('opl/opl/executor.py', 'r')
compiledExecutor = lzma.compress(marshal.dumps(compile(f.read(), 'executor', 'exec')))
f.close()

f = open('opl/oplos/operatingsystem.py', 'r')
compiledSystem = lzma.compress(marshal.dumps(compile(f.read(), 'operatingsystem', 'exec')))
f.close()

f = open('system.sys', 'wb')
f.write(compiledSystem)
f.close()

f = open('sysopl.sys', 'wb')
f.write(compiledExecutor)
f.close()