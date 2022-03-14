from lxml import etree
import soundfile as sf 
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt



RL = {
    1: "Right Outer Main Beam",
    2: 'Right Inner Main Beam',
    3: 'Right Signature',
    4: 'Right Channel 4',
    5: 'Right Channel 5',
    6: 'Right Channel 6',
    7: 'Right Front Turn',
    8: 'Right Front Fog',
    9: 'Right Aux Park',
    10: 'Right Side Marker',
    11: 'Right Side Repeater',
    12: 'Right Rear Turn',
    13: 'Right Tail',

}

LL = {
    1: 'Left Outer Main Beam',
    2: 'Left Inner Main Beam',
    3: 'Left Signature',
    4: 'Left Channel 4',
    5: 'Left Channel 5',
    6: 'Left Channel 6',
    7: 'Left Front Turn',
    8: 'Left Front Fog',
    9: 'Left Aux Park',
    10: 'Left Side Marker',
    11: 'Left Side Repeater',
    12: 'Left Rear Turn',
    13: 'Left Tail',
}

BL = {
    7: 'Brake Lights',
    8: 'License Plate',
}
AL = list(RL.values()) + list(LL.values()) + list(BL.values())
DR = {
    1: "Liftgate",
}

data, samplerate = sf.read('mass.wav') 

data = data[:, 0] + data[:, 1]
data = data.reshape(-1)
pd = data * data
N = 441
data = np.convolve(pd, np.ones(N)/N, mode='valid')
peaks, _ = find_peaks(data, distance=441 * 20, height=0.2)


plt.plot(data)
plt.plot(peaks, data[peaks], "x")
plt.show()

newSeq = etree.parse('template.xsq') 
root = newSeq.getroot()

def appendToNodes(element, nodes):
    for nodeName in nodes:
        new_element = etree.fromstring(etree.tostring(element))
        node = root.find(".//Node[@name='" + nodeName + "']")
        if node is None:
            print("XX", nodeName)
        node.append(new_element)

def onFor(name, start, on_for, pl=0):
    appendToNodes(etree.fromstring(f'<Effect ref="{pl}" name="On" startTime="' + str(int(start)) + '" endTime="' + str(int(start + on_for)) + '" palette="0"/>'), name)

l = 0
NL = 13
for i in range(len(peaks)):
    t = peaks[i] / 44100 * 1000
    t_1 = data.shape[0] / 44100 * 1000
    if i + 1 < len(peaks):
        t_1 = peaks[i + 1] / 44100 * 1000
    
    if t < 85000:
        onFor([LL[1 + i % NL ], RL[1 + i%NL], LL[1 + (i + 1) % NL ], RL[1 + (i + 1) %NL]], t, t_1 - t)
        l += 1
for i in range(15):
    onFor(AL, 85000 + i * 400, 200)

for i in range(len(peaks)):
    t = peaks[i] / 44100 * 1000
    t_1 = data.shape[0] / 44100 * 1000
    if i + 1 < len(peaks):
        t_1 = peaks[i + 1] / 44100 * 1000

    if t > 92000:
        onFor([LL[1 + i % NL ], RL[1 + i%NL], LL[1 + (i + 1) % NL ], RL[1 + (i + 1) %NL], LL[1 + (i + 2) % NL ], RL[1 + (i + 2) %NL], LL[1 + (i + 3) % NL ], RL[1 + (i + 3) %NL]], t, t_1 - t)
        l += 1
    
onFor(["Left Rear Window"], 11000, 10000, 1)
newSeq.write("mass.xsq")
