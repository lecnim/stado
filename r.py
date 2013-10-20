class dec:

    functions = {}

    def __call__(self, path):
        def wrap(function):
            self.functions[path] = function
        return wrap


f = dec()



@f('ok')
def i(a):
    print(a)
@f('okb')
def b(a):
    print(a)
@f('okd')
def c(a):
    print(a)

print(f.functions)

for i, k in f.functions.items():
    k(i)
