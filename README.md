```
 _ __  ___ _   _  ___ __ _|*| ___ 
| '_ \/ __| | | |/ __/ _` | |/ __|
| |_) \__ \ |_| | (_| (_| | | (__ 
| .__/|___/\__,_|\___\__,_|_|\___|
|_| ------------------------- v0.1
psu hierarchy and current modeler.
(c) 2023 a10k, Inc. <root@a10k.co>
==================================

Usage: psucalc [config.py]

 * component 

Components are used to model a power supply's load.

component([name], [A=A(n)], [W=W(n)], [duty=duty(n)], qty=n], ...)

A <-> A(*): Amperage consumed by this component
W <-> W(*): Wattage consumed by this component
duty <-> duty(1.0): Duty Cycle decimal
label <-> label(''): Part classifier
qty <-> qty(1): Component Quantity

IC
Inherits: component
Used to represent one or more Integrated Circuits.

OPAmp
Inherits: component
Used to represent one or more Operational Amplifiers.
duty <-> duty(0.5): Duty Cycle decimal

Audio_OPAmp
Inherits: OPAmp
Used to represent one or more Audio Amplifiers.
duty <-> duty(0.3): Duty Cycle decimal

 * psu 

Power Supply Units are used to form the model's hierarchy.

psu(name, [Vout=V(n)], [effc=effc(0.n)], ..., subs=[component, ...])

A <-> A(*): Input amperage
Vdrop <-> V(*): Voltage drop from input to output
Vin <-> V(*): Input voltage
Vout <-> V(*): Output voltage
W <-> W(*): Disspipation
Win <-> W(*): Input wattage
Wout <-> W(*): Output wattage
effc <-> effc(*): Efficiency of the conversion
ratio <-> ratio(*): Conversion ratio
subs <-> branch([]): Components drawing from this PSU

AC_Mains
Inherits: psu
Unregulated AC input
Vin <-> V(120.0): Volt

Transformer
Inherits: psu
Step-down transformer
effc <-> effc(0.98): Efficiency decimal

Bridge_Rectifier
Inherits: psu
Full-wave bridge rectifier
drop <-> V(0.7): Volt

Buck
Inherits: psu
Buck converter
effc <-> effc(0.9): Efficiency decimal
freq <-> Hz(0.2): Switching frequency
trans <-> s(5e-05): Switching transition time

Buck_Inverting
Inherits: Buck
Buck-boost converter
effc <-> effc(0.85): Efficiency decimal

Flyback
Inherits: Buck
Flyback converter
effc <-> effc(0.85): Efficiency decimal
freq <-> Hz(0.1): Hertz
trans <-> s(0.0001): Second

Linear
Inherits: psu
Linear regulator
dropout <-> V(2.0): Dropout voltage

Linear_Inverting
Inherits: Linear
None

LDO_Linear_Inverting
Inherits: Linear_Inverting
Low-dropout linear regulator (inverting)
dropout <-> V(0.5): Volt

LDO_Linear
Inherits: Linear
Low-dropout linear regulator
dropout <-> V(0.5): Volt

 * units 

label -> label`: Descriptive Label
qty -> qty`: Component Quantity
V -> V`: Volt
mV -> V`: Millivolt
A -> A`: Ampere
mA -> A`: Milliampere
W -> W`: Watt
s -> s`: Second
us -> s`: Microsecond
ms -> s`: Millisecond
Hz -> Hz`: Hertz
kHz -> Hz`: Kilohertz
MHz -> Hz`: Megahertz
C -> C`: Farad
uF -> C`: Microfarad
nF -> C`: Nanofarad
pF -> C`: Picofarad
L -> L`: Henry
uH -> L`: Microhenry
nH -> L`: Nanohenry
pH -> L`: Picohenry
percent -> percent`: Percent decimal
P -> percent`: Percent number
duty -> duty`: Duty Cycle decimal
effc -> effc`: Efficiency decimal
ratio -> ratio`: Conversion Ratio decimal
R -> ratio`: Conversion Ratio n:m
```

## Example Config
```
AC_Mains(Vout=V(120), subs=[
    #Transformer(ratio=R('1:6'), subs=[
    Transformer(Vout=V(24), subs=[
        Bridge_Rectifier(subs=[
            Buck(Vout=V(17.5), subs=[
                Buck(Vout=V(3.3), subs=[
                    IC('STM32', A=mA(660)), 
                    IC('PCM3168', A=mA(130)), 
                ]),
                Buck(Vout=V(3.3), subs=[
                    IC('LAN8720A', W=mW(200)), 
                ]),
                Buck(Vout=V(5.6), subs=[
                    LDO_Linear(Vout=V(5), subs=[
                        IC('PCM3168', A=mA(210)), 
                    ]), 
                ]), 
                Linear(Vout=V(15), subs=[
                    Audio_OPAmp('THAT_1606Q', qty=8, A=mA(620)), 
                    Audio_OPAmp('THAT_1646W', qty=6, A=mA(620)), 
                ]),
                Buck_Inverting(Vout=V(-16.5), subs=[
                    LDO_Linear_Inverting(Vout=V(-15), subs=[
                        Audio_OPAmp('THAT_1606Q', qty=8, A=mA(620)), 
                        Audio_OPAmp('THAT_1646W', qty=6, A=mA(620)), 
                    ]), 
                ]),
            ]),
        ]),
    ]),
])
```
