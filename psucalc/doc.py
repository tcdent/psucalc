from inspect import getmembers
from psucalc import *

class doc(object):
    class unit(object):
        def __init__(self, cls, _doc=None):
            self.cls = cls
            if _doc: self.cls.__doc__ = _doc
            if hasattr(cls, '__annotations__') and cls.__annotations__:
                self._type = cls.__annotations__.get('return').__name__
            else:
                self._type = cls.__name__
        
        def __repr__(self):
            return "".join((
                "{BLD}{PNK}{name}{RST} ", 
                "{DIM}->{RST} {PNK}{unit}{RST}`: ", 
                "{doc}",
            )).format(**{
                "name": self.cls.__name__, 
                "unit": self._type,
                "doc": self.cls.__doc__, 
            }, **ANSI)
    
    class attr(object):
        def __init__(self, cls, k, v):
            self.cls, self.k, self.v = cls, k, v
            self._type = v.__class__
            if isinstance(v, property):
                ret_type = v.fget.__annotations__.get('return', None)
                if ret_type: self._type = ret_type
                self.default = '*'
            else:
                self.default = repr(getattr(self.cls, self.k))
            self._unit = self._type.__name__
            if self._type.__name__ == 'str': self._unit = 'str'
            if self._type.__name__ == 'list': self._unit = 'list'
            
        def __repr__(self):
            return "".join((
                "{BLD}{k}{RST} ", 
                "{DIM}<->{RST} {PNK}{unit}{RST}({default}): ", 
                "{doc}\n", 
            )).format(**{
                "k": self.k, 
                "unit": self._unit,
                "default": self.default,
                "doc": self.v.__doc__, 
            }, **ANSI)

    def __init__(self, cls, parent=None):
        self.parent = parent
        self.cls = cls
        self.subs = list()
        
        self.attrs = list()
        for k, v in getmembers(self.cls):
            if k.startswith('_'): continue
            if not k: continue
            attr = doc.attr(cls, k, v)
            if self._attr_listed(attr): continue
            if self.parent and self.parent._attr_listed(attr): continue
            self.attrs.append(attr)
        for sub in self.cls.__subclasses__():
            sub = doc(sub, self)
            self.subs.append(sub)
    
    def _attr_listed(self, attr):
        for a in self.attrs:
            if a.k == attr.k and a.default == attr.default:
                return True
        if self.parent is not None and self.parent._attr_listed(attr):
            return True
        return False

    def __repr__(self):
        docstr = "\n".join((
            "{BLD}{CYN}{name}{RST}" if self.parent else "{REV}{PNK} * {name} {RST}", 
            "{ITL}{parent}{RST}", 
            "{doc}", 
            "{attrs}", 
        )).format(**dict(
            name=self.cls.__name__, 
            parent="Inherits: %s" % self.parent.cls.__name__ if self.parent else "", 
            doc=self.cls.__doc__, 
            attrs="".join(repr(a) for a in self.attrs) + "\n", 
        ), **ANSI)
        for sub in self.subs:
            docstr += repr(sub)
        return docstr

units = [doc.unit(k, v) for k, v in (
    (label, "Descriptive Label"), 
    (qty, "Component Quantity"),
    (V, "Volt"),
    (mV, "Millivolt"),
    (A, "Ampere"),
    (mA, "Milliampere"),
    (W, "Watt"),
    (s, "Second"),
    (us, "Microsecond"),
    (ms, "Millisecond"),
    (Hz, "Hertz"),
    (kHz, "Kilohertz"),
    (MHz, "Megahertz"),
    (C, "Farad"),
    (uF, "Microfarad"),
    (nF, "Nanofarad"),
    (pF, "Picofarad"),
    (L, "Henry"),
    (uH, "Microhenry"),
    (nH, "Nanohenry"),
    (pH, "Picohenry"),
    (percent, "Percent decimal"),
    (P, "Percent number"),
    (duty, "Duty Cycle decimal"),
    (effc, "Efficiency decimal"),
    (ratio, "Conversion Ratio decimal"),
    (R, "Conversion Ratio n:m"),
)]

component.__doc__ = """\
Components are used to model a power supply's load.

{PNK}{ITL}component{RST}([{BLD}name{RST}], [{BLD}A{RST}=A({ITL}n{RST})], [{BLD}W{RST}=W({ITL}n{RST})], [{BLD}duty{RST}=duty({ITL}n{RST})], {BLD}qty{RST}={ITL}n{RST}], ...)
""".format(**ANSI)
component.W.__doc__ = "Wattage consumed by this component"
component.A.__doc__ = "Amperage consumed by this component"
component.label.__doc__ = "Part classifier"

IC.__doc__ = "Used to represent one or more Integrated Circuits."
OPAmp.__doc__ = "Used to represent one or more Operational Amplifiers."
Audio_OPAmp.__doc__ = "Used to represent one or more Audio Amplifiers."

psu.__doc__ = """\
Power Supply Units are used to form the model's hierarchy.

{PNK}{ITL}psu{RST}({BLD}name{RST}, [{BLD}Vout{RST}=V({ITL}n{RST})], [{BLD}effc{RST}=effc({ITL}0.n{RST})], ..., {BLD}subs{RST}=[{ITL}component{RST}, ...])
""".format(**ANSI)
psu.A.__doc__ = "Input amperage"
psu.W.__doc__ = "Disspipation"
psu.Win.__doc__ = "Input wattage"
psu.Wout.__doc__ = "Output wattage"
psu.Vin.__doc__ = "Input voltage"
psu.Vout.__doc__ = "Output voltage"
psu.Vdrop.__doc__ = "Voltage drop from input to output"
psu.effc.__doc__ = "Efficiency of the conversion"
psu.ratio.__doc__ = "Conversion ratio"
psu.subs.__doc__ = "Components drawing from this PSU"

AC_Mains.__doc__ = "Unregulated AC input"
Transformer.__doc__ = "Step-down transformer"
Bridge_Rectifier.__doc__ = "Full-wave bridge rectifier"
Buck.__doc__ = "Buck converter"
Buck.freq.__doc__ = "Switching frequency"
Buck.trans.__doc__ = "Switching transition time"
Buck_Inverting.__doc__ = "Buck-boost converter"
Flyback.__doc__ = "Flyback converter"
Linear.__doc__ = "Linear regulator"
Linear.dropout.__doc__ = "Dropout voltage"
LDO_Linear.__doc__ = "Low-dropout linear regulator"
LDO_Linear_Inverting.__doc__ = "Low-dropout linear regulator (inverting)"

__doc__ = """\
{DIM}Usage:{RST} {BLD}psucalc{RST} {ITL}[config.py]{RST}

{component}{psu}\
{REV}{BLU} * units {RST}

{units}
""".format(**{
    "psu": doc(psu), 
    "component": doc(component), 
    "units": "\n".join(repr(u) for u in units),
}, **ANSI)

