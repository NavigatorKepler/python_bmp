from struct import unpack


class BMPException(BaseException):
    pass


errors_en = [
    'File Not Found!',
    'Not a valid BMP file!',
    "Unsupported Format!",
    "Compression Not Supported!",
]

errors_cn = [
    '找不到文件！',
    '文件无效！',
    "格式不支持！",
    "暂不支持压缩。",
]


class BMP(object):
    def __init__(self, filename, lang='cn'):
        self.__filename = filename
        if lang == 'en':
            self.__errors = errors_en
        elif lang == 'cn':
            self.__errors = errors_cn
        else:
            self.__errors = errors_cn
        self.__bmpprocess(filename)

    def __bmpprocess(self, filename):
        try:  # upy下无法用os直接判断文件是否存在，故try
            with open(self.__filename, 'rb') as f:
                self.__stream = f.read()
        except:
            raise BMPException(self.__errors[0])

        # 文件头部分
        self.__bfType = unpack("<h", self.__stream[0:2])[0]         # BM标识
        if self.__bfType != 0x4d42:
            raise BMPException(self.__errors[1])

        self.__bfSize = unpack("<i", self.__stream[2:6])[0]         # 文件大小
        # self.__bfRsv1 = unpack("<h", self.__stream[6:8])[0]         # 保留字段
        # self.__bfRsv2 = unpack("<h", self.__stream[8:10])[0]        # 保留字段
        self.__bfOffBits = unpack("<i", self.__stream[10:14])[0]    # 偏移量
        # print(self.__bfOffBits)

        # 信息头部分
        self.__biSize = unpack("<i", self.__stream[14:18])[0]       # 信息头大小
        if self.__biSize not in (40, 108, 124):
            raise BMPException(self.__errors[2])

        self.__biWidth = unpack("<i", self.__stream[18:22])[0]      # 宽度

        self.__biHeight = unpack("<i", self.__stream[22:26])[0]     # 高度
        if self.__biHeight > 0:
            self.__hreversed = True  # 高度反序
        else:
            self.__hreversed = False  # 高度顺序

        # self.__biPlains = unpack("<h", self.__stream[26:28])[0]     # 颜色平面数总为1
        self.__biBitCount = unpack("<h", self.__stream[28:30])[0]   # 每像素比特数
        if self.__biBitCount != 24:
            raise BMPException(self.__errors[2])

        self.__biCompression = unpack("<i", self.__stream[30:34])[0]  # 图像压缩类型
        if self.__biCompression != 0:
            raise BMPException(self.__errors[3])

        self.__biSizeImage = unpack("<i", self.__stream[34:38])[0]    # 图像大小
        # self.__biXPelsPerMeter = unpack("<i", self.__stream[38:42])[0]  # 水平像素密度
        # self.__biYPelsPerMeter = unpack("<i", self.__stream[42:46])[0]  # 垂直像素密度
        # self.__biClrUsed = unpack("<i", self.__stream[46:50])[0]      # 索引色数
        # self.__biClrImportant = unpack("<i", self.__stream[50:54])[0]  # 重要索引色数
        self.__bmp_data = []

        self.__bitmap_stream = self.__stream[self.__bfOffBits:]

        del self.__stream

        self.__temp_cursor = 0
        for height in range(self.__biHeight):
            bmp_data_row = []
            # 四字节填充位检测
            count = 0
            for width in range(self.__biWidth):
                ready_pixel = (self.__bitmap_stream[self.__temp_cursor + 2],  # R
                                     self.__bitmap_stream[self.__temp_cursor + 1],  # G
                                     self.__bitmap_stream[self.__temp_cursor])  # B
                bmp_data_row.append(ready_pixel)
                count += 3
                self.__temp_cursor += 3
            # bmp 四字节对齐原则
            while count % 4 != 0:
                count += 1
                self.__temp_cursor += 1
            self.__bmp_data.append(bmp_data_row)
        if self.__hreversed:
            self.__bmp_data.reverse()
        # R, G, B 三个通道
        self.__R = []
        self.__G = []
        self.__B = []

        for row in range(self.__biHeight):
            R_row = []
            G_row = []
            B_row = []
            for col in range(self.__biWidth):
                R_row.append(self.__bmp_data[row][col][0])
                G_row.append(self.__bmp_data[row][col][1])
                B_row.append(self.__bmp_data[row][col][2])
            self.__B.append(B_row)
            self.__G.append(G_row)
            self.__R.append(R_row)

        del self.__bitmap_stream

    def __len__(self):
        return self.__biSizeImage

    def width(self):
        return self.__biWidth

    def height(self):
        return self.__biHeight

    def get_B(self):
        return self.__B

    def get_G(self):
        return self.__G

    def get_R(self):
        return self.__R

    def get_pixels(self):
        return self.__bmp_data

a = BMP('0.bmp')
print(a.get_pixels()[0])