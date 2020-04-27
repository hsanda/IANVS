import struct

_packstr = "<1I"  # unsigned 32-bit integer


class UA32():
    def __init__(self, a):
        self.a = bytearray(a)

    def __getitem__(self, k):
        return struct.unpack_from(_packstr, self.a, k * 4)[0]

    def __setitem__(self, k, v):
        struct.pack_into(_packstr, self.a, k * 4, v)

    def copy(self):
        return UA32(self.a[:])

    def into(self, d):
        d.a[:] = self.a[:]

    def raw(self):
        return self.a