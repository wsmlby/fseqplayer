from player import FSeqPlayer, ChannelType


p = FSeqPlayer("im.fseq", "im.wav")
p.prepare_channel(channel_type_callback=lambda x: ChannelType.TRANSITION if x == 2 else ChannelType.NOOP)
p.play(lambda x, y: print(f"change channel {x} to {y}"))