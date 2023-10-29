# -*- coding: utf8 -*-
# written for Python 3.8.2
from math import *

MOTD = """
{PNK} _ __  ___ _   _  ___ __ _|*| ___ 
{PNK}| '_ \/ __| | | |/ __/ _` | |/ __|
{PNK}| |_) \__ \ |_| | (_| (_| | | (__ 
{PNK}| .__/|___/\__,_|\___\__,_|_|\___|
{PNK}|_| ------------------------- {RST}{BLD}v0.1{RST}
{DIM}{ITL}psu hierarchy and current modeler.{RST}
{DIM}(c) 2023 a10k, Inc. {UDL}<root@a10k.co>{RST}
{DIM}=================================={RST}
"""

ANSI = dict([
    (v, "\033[%sm" % i) for v, i in \
        list(zip(['RST', 'BLD', 'DIM', 'ITL', 'UDL', 'SBL', 'FBL', 'REV'], range(8))) + \
        list(zip(['BLK', 'RED', 'GRN', 'YEL', 'BLU', 'PNK', 'CYN', 'WHT'], range(30, 38)))
])

class label(str): pass
class qty(int): pass
class nullable(float):
    def __new__(cls, i):
        if i is None: return None
        return super().__new__(cls, i)

class V(nullable): pass
def mV(i) -> V: return V(i / 1000.0)

class A(nullable): pass
def mA(i) -> A: return A(i / 1000.0)

class W(nullable): pass
def mW(i) -> W: return W(i / 1000.0)

class s(nullable): pass
def us(i) -> s: return s(i / 1000000.0)
def ms(i) -> s: return s(i / 1000.0)

class Hz(nullable): pass
def kHz(i) -> Hz: return Hz(i / 1000.0)
def MHz(i) -> Hz: return Hz(i / 1000000.0)

class C(nullable): pass
def uF(i) -> C: return C(i / 1000000.0)
def nF(i) -> C: return C(i / 1000000000.0)
def pF(i) -> C: return C(i / 1000000000000.0)

class L(nullable): pass
def uH(i) -> L: return L(i / 1000000.0)
def nH(i) -> L: return L(i / 1000000000.0)
def pH(i) -> L: return L(i / 1000000000000.0)

class percent(nullable): pass
def P(i) -> percent: return percent(i / 100.0)

class ratio(percent): pass
def R(ratio_str="1:1") -> ratio:
    fm, to = ratio_str.split(':')
    return ratio(float(fm) / float(to))

class duty(percent): pass
class effc(percent): pass



class propertize(type):
    def __new__(cls, name, bases, attrs):
        for k, v in attrs.items():
            if not '__' in k and callable(v):
                attrs[k] = property(v)
        return super().__new__(cls, name, bases, attrs)

class branch(list, metaclass=propertize):
    def W(self) -> W:
        return sum(map(lambda x: x.W or 0.0, self))

class tree(object, metaclass=propertize):
    _parent = None

    def __init__(self, **kwargs):
        self.subs = branch(kwargs.pop('subs', []))
        for x in self.subs:
            x._parent = self
    
    def __call__(self):
        print(self)
    
    def _depth(self):
        if not self._parent: return 0
        return self._parent._depth + 1

    def _warns(self):
        return []

class component(tree):
    label = label("")
    qty = qty(1)
    duty = duty(1.0)

    def __init__(self, name, **kwargs):
        self.label = label(name or self.label)
        self.qty = qty(kwargs.pop('qty', self.qty))
        self.duty = duty(kwargs.pop('duty', self.duty))
        self._watts = W(kwargs.pop('W', None))
        self._amps = A(kwargs.pop('A', None))
        super().__init__()

    def __repr__(self):
        return " ".join((
            "{BLU}{label}{RST}{qty}", 
            "{DIM}{A:.2f}A{RST}", 
            "{DIM}{W:.2f}W{RST}", 
        )).format(**{
            'W': self.W, 
            'A': self.A, 
            'label': self.label, 
            'qty': " (x%s)" % self.qty if self.qty > 1 else "", 
        }, **ANSI)

    def W(self) -> W:
        if self._watts is not None:
            return self._watts * self.qty * self.duty
        return self.A * abs(self._parent.Vout)

    def A(self) -> A:
        if self._amps is not None:
            return self._amps * self.qty * self.duty
        return self.W / abs(self._parent.Vout)

class psu(tree):
    subs = branch()

    def __init__(self, **kwargs):
        self._Vin = V(kwargs.pop('Vin', None))
        self._Vout = V(kwargs.pop('Vout', None))
        self._ratio = ratio(kwargs.pop('ratio', None))
        self._effc = effc(kwargs.pop('effc', None))
        super().__init__(**kwargs)

    def __repr__(self):
        return " ".join((
                "{BLD}{REV} {Vout:+.1f}V {RST}", 
                "{PNK}{A:.2f}A{RST}", 
                "{CYN}{W:.1f}W", 
                "{BLD}{name}{RST}", 
                "{effc_color}{effc:.0%}{RST}", 
                "{DIM}{Vdrop:+.1f}V{RST}", 
                "{DIM}{ratio:.1f}:1{RST}", 
                "{RED}{REV}{warns}{RST}{subs}",
            )).format(**{
                'Vout': self.Vout, 
                'A': self.A, 
                'W': self.Wout, 
                'name': self.__class__.__name__, 
                'effc': self.effc, 
                'effc_color': ANSI[('RED', 'YEL', 'GRN')[min(max(int(self.effc * 10 - 7), 0), 2)]], 
                'Vdrop': self.Vdrop, 
                'ratio': self.ratio, 
                'warns': ''.join(["\n%s %s" % (">>>" * self._depth, w) for w in self._warns]), 
                'subs':  ''.join(["\n%s├─%s" % ("│  " * self._depth, repr(s)) for s in self.subs]), 
            }, **ANSI)

    def _warns(self):
        ws = super()._warns
        if self.effc < 0.8:
            ws.append("efficiency < 80%")
        return ws
    
    def ratio(self) -> ratio:
        if self._ratio is not None:
            return self._ratio
        if not self._parent:
            return ratio(1)
        return ratio(abs(self.Vin) / abs(self.Vout))

    def effc(self) -> effc:
        if self._effc is not None:
            return self._effc
        if not self._parent:
            return 1.0
        return 0 #return abs(self.Wout / self.Win)

    def A(self) -> A:
        return A(self.Wout / abs(self.Vout))
    
    def W(self) -> W:
        return self.Win

    def Win(self) -> W:
        return W(self.subs.W / self.effc)

    def Wout(self) -> W:
        return self.subs.W

    def Vin(self) -> V:
        if self._Vin is not None:
            return self._Vin
        if not self._parent:
            return self.Vout
        return V(self._parent.Vout)

    def Vout(self) -> V:
        if self._Vout is not None:
            return self._Vout
        if not self._parent:
            return self.Vin
        return V(self._parent.Vout * self.ratio)

    def Vdrop(self) -> V:
        return V(self.Vin - self.Vout)


class IC(component):
    pass

class OPAmp(component):
    duty = duty(0.5)

class Audio_OPAmp(OPAmp):
    duty = duty(0.3)


class AC_Mains(psu):
    Vin = V(120)

class Transformer(psu):
    effc = effc(0.98)

class Bridge_Rectifier(psu):
    drop = mV(700) # drop per diode

    def effc(self) -> effc:
        return effc(1 - (self.A * (2 * self.drop)) / self.Wout)

    def Vout(self) -> V:
        return V(sqrt(2) * self.Vin - 2 * self.drop)

class Buck(psu):
    effc = effc(0.9)
    freq = kHz(200) # switching
    trans = us(50) # transition

    def Wout(self) -> W:
        w = super().Wout
        return W(w - (w * self.freq * self.trans))

class Buck_Inverting(Buck):
    effc = effc(0.85)

class Flyback(Buck):
    effc = effc(0.85)
    freq = kHz(100)
    trans = us(100)

class Linear(psu):
    dropout = V(2)

    def _warns(self):
        ws = super(Linear, self)._warns
        if not abs(self.Vout) + self.dropout < abs(self._parent.Vout):
            ws.append("dropout voltage exceeded")
        return ws

    def effc(self) -> effc:
        return effc(abs(self.Vout) / abs(self._parent.Vout))

class Linear_Inverting(Linear):
    pass

class LDO_Linear(Linear):
    dropout = V(0.5)

class LDO_Linear_Inverting(Linear_Inverting):
    dropout = V(0.5)

