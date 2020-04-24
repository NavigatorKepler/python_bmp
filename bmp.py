class BMPException(BaseException):
    pass

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

        try:                #无法判断文件是否存在，只能try
            with open(self.__filename, 'rb') as f:
                img_bytes = list(bytearray(f.read()))
        except : raise BMPException("File Not Found!")