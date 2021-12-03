from django.test import TestCase

class Test:

    def __init__(self,ar0, ar1 = '1'):
        self.ar0 = ar0
        self.ar1 = ar1

    def __str__(self):
        return f"{self.ar0} - {self.ar1}"

    def uptodate(self, ar0 = None, ar1 = None):
        if ar0 != None:
            self.ar0 = ar0
        if ar1 != None:
            self.ar1 = ar1

# Create your tests here.

t1 = Test('2', '6')
t2 = Test(1)
print(f't1 - {t1}')
print(f't2 - {t2}')
t2.ar1 = 29
t2.uptodate('0', '1')
print(f't2 - {t2}')
t1.uptodate(t2.ar0)
print(f't1 - {t1}')
t1.uptodate(ar1='1')
print(f't1 - {t1}')

