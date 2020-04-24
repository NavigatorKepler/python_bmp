class BMP(object):
    def __init__(self, filename):
        self.__filename = filename
        self.__data = self.__bmpprocess(filename)
    
    def __bmpprocess(self, filename):
        def little_endian_bytes_to_int(bytes):      #小端转整数
            n = 0x00
            while len(bytes) > 0:
                n <<= 8
                n |= bytes.pop()
            return int(n)

        import os
        assert os.exist(filename), 'No Such File.'
        
        with open(self.__filename, 'rb') as f:
            img_bytes = list(bytearray(f.read()))