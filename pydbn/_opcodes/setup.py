from distutils.core import setup, Extension

module1 = Extension('_opcodes', sources = ['opcodes.c'])

setup (description = 'interpreter opcodes in c',   ext_modules = [module1])
