import sys 
import runpy
import types
# TIL: module.__builtins__ is just an implementation detail
import builtins

# If you don't know what the qualified name is:
# https://docs.python.org/3/glossary.html#term-qualified-name

class BinLaden:
    def __init__(self):
        # "Things" yet to override
        # Once they have been overriden thre is no need to keep em around
        # since sys.modules is a thing.
        # If you want to have "selective" override keeping the original module
        # might be necessary to avoid reimporting every time
        # This dict maps qualified name -> "thing"
        self.to_override = {}
        self.hijack()

    def __import__(self, name, globals_=None, locals_=None, fromlist=(), level=0):
        module = self.import_(name, globals_, locals_, fromlist, level)

        for qualname, obj in self.to_override.copy().items():
            if not qualname[0] == module.__name__:
                continue

            foo = module
            for name in qualname[1:-1]:
                if not hasattr(foo, name):
                    break
                foo = getattr(module, name)
            else:
                if hasattr(foo, qualname[-1]):
                    setattr(foo, qualname[-1], obj)
                    self.to_override.pop(qualname)

        return module 

    def hijack(self):
        self.import_ = builtins.__import__
        builtins.__import__ = self.__import__
    
    def restore(self):
        builtins.__import__ = self.import_

    def run(self, file):
        runpy.run_path(file, run_name="__main__")

    def runmodule(self, path):
        sys.modules.pop("__main__")
        runpy.run_module(path, run_name="__main__")

    def override(self, qualname, obj=None):
        if obj:
            self.to_override[tuple(qualname.split("."))] = obj
            return
        
        def _(fun):
            self.to_override[tuple(qualname.split("."))] = fun
            return fun

        return _ 
