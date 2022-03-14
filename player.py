from typing import Callable, List
import fseq
from enum import Enum
import pyaudio
import wave

class ParamError(Exception):
    pass


class ChannelType(Enum):
    UNKNOWN = -1
    NOOP = 0
    TRANSITION = 1 # the callback will be (channel, change_to_state)

def _run(channel_type_callback, seq, channel):
    import time
    channel_type_callback(channel, seq[0][1])
    for i in range(1, len(seq)):
        time.sleep((seq[i][0] - seq[i - 1][0]) / 1000)
        channel_type_callback(channel, seq[i][1])

def playx(self):
    chunk = 2048
    data = self.wf.readframes(chunk)
    while data != '':
        if len(data) == 0:
            break
        self.stream.write(data)
        data = self.wf.readframes(chunk)
    
class FSeqPlayer:
    def __init__(self, fseq_file: str, music_path: str = None) -> None:       
        f = open(fseq_file, "rb")
        fq = fseq.parse(f)
        self.number_of_channel = fq.channel_count_per_frame
        fd = []
        for i in range(fq.number_of_frames):
            d = fq.get_frame(i)
            fd.append(d)
        self.data = fd
        self._step_time_in_ms = fq.step_time_in_ms

        music_path = music_path
        if music_path == None:
            found = False
            for key, value in fq.variable_headers:
                if key == 'mf':
                    music_path = value
                    found = True
            if not found:
                raise ParamError("music_path not found in fseq, you need to supply on in param here")
        self.wf = wave.open(music_path, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format =
                self.p.get_format_from_width(self.wf.getsampwidth()),
                channels = self.wf.getnchannels(),
                rate = self.wf.getframerate(),
                output = True)
        self.channel_types = [ChannelType.UNKNOWN for i in range(self.number_of_channel)]
        
    def prepare_channel(self, channel_types: List[ChannelType] = None, channel_type_callback: Callable[[int], ChannelType] = None):
        if channel_types != None:
            assert len(channel_types) == self.number_of_channel
            self.channel_types = channel_types
        else:
            for i in range(self.number_of_channel):
                self.channel_types[i] = channel_type_callback(i)
        self.trigger_channels = set()

        self.seq = {}
        for j in range(self.number_of_channel):
            if self.channel_types[j] == ChannelType.TRANSITION:
                self.trigger_channels.add(j)
                last = self.data[0][j]
                self.seq[j] = []
                self.seq[j].append((0, last))
                for i in range(1, len(self.data)):
                    t = self._step_time_in_ms * i
                    d = self.data[i][j]
                    if d != last:
                        self.seq[j].append((t, d))
                        last = d
    

    def play(self, channel_type_callback: Callable[[int, int], None]):
        import threading
        threads = []
        for j in self.trigger_channels:
            threads.append(threading.Thread(target=_run, args=[channel_type_callback, self.seq[j], j]))
        
        threads.append(threading.Thread(target=playx, args=[self]))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
