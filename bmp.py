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
    def __init__(self, filename, lang='cn') :
        self.__filename = filename
        self.__data = self.__bmpprocess(filename)
        if lang == 'en':
            self.__errors = errors_en
        elif lang == 'cn':
            self.__errors = errors_cn
        else:
            self.__errors = errors_cn

    def __bmpprocess(self, filename):
        try:                #无法判断文件是否存在，只能try
            with open(self.__filename, 'rb') as f:
                self.__stream = f.read()
        except : raise BMPException(self.__errors[0])

        # 读取 bmp 文件的文件头    14 字节
        self.__bfType = unpack("<h", self.__stream[0:2])[0]       # 0x4d42 对应BM 表示这是Windows支持的位图格式
        if self.__bfType != 0x4d42:
            raise BMPException(self.__errors[1])

        self.__bfSize = unpack("<i", self.__stream[2:6])[0]         # 位图文件大小
        self.__bfRsv1 = unpack("<h", self.__stream[6:8])[0]         # 保留字段 必须设为 0
        self.__bfRsv2 = unpack("<h", self.__stream[8:10])[0]        # 保留字段 必须设为 0
        self.__bfOffBits = unpack("<i", self.__stream[10:14])[0]    
            # 偏移量 从文件头到位图数据需偏移多少字节

        # 读取 bmp 文件的位图信息头 40 字节
        self.__biSize = unpack("<i", self.__stream[14:18])[0]       # 所需要的字节数
        if self.__bfSize != 40:
            print(self.__bfSize)
            raise BMPException(self.__errors[2])

        self.__biWidth = unpack("<ib", self.__stream[18:22])[0]      # 图像的宽度 单位 像素

        self.__biHeight = unpack("<ib", self.__stream[22:26])[0]     # 图像的高度 单位 像素
        if self.__biHeight > 0 : self.__hreversed = True       #高度反序
        else : self.__hreversed = False                        #高度顺序

        self.__biPlains = unpack("<h", self.__stream[26:28])[0]     # 说明颜色平面数 总设为 1
        self.__biBitCount = unpack("<h", self.__stream[28:30])[0]   # 说明每像素比特数
        if self.__biBitCount != 24:
            raise BMPException(self.__errors[2])
        
        
        self.__biCompression = unpack("<i", self.__stream[30:34])[0]  # 图像压缩的数据类型
        if self.__biCompression != 0:
            raise BMPException(self.__errors[3])

        self.__biSizeImage = unpack("<i", self.__stream[34:38])[0]    # 图像大小
        self.__biXPelsPerMeter = unpack("<i", self.__stream[38:42])[0]# 水平分辨率
        self.__biYPelsPerMeter = unpack("<i", self.__stream[42:46])[0]# 垂直分辨率
        self.__biClrUsed = unpack("<i", self.__stream[46:50])[0]      # 实际使用的彩色表中的颜色索引数
        self.__biClrImportant = unpack("<i", self.__stream[50:54])[0] # 对图像显示有重要影响的颜色索引的数目
        self.__bmp_data = []

        self.__bitmap_stream = self.__stream[54:]
        self.__temp_cursor = 0
        for height in range(self.__biHeight) :
            bmp_data_row = []
            # 四字节填充位检测
            count = 0
            for width in range(self.__biWidth) :
                bmp_data_row.append([unpack("<B", self.__bitmap_stream[self.__temp_cursor])[0],     #B
                                     unpack("<B", self.__bitmap_stream[self.__temp_cursor + 1])[0],     #G
                                     unpack("<B", self.__bitmap_stream[self.__temp_cursor + 2])[0]])    #R
                count += 3
                self.__temp_cursor += 3
            # bmp 四字节对齐原则
            while count % 4 != 0 :
                count += 1
                self.__temp_cursor += 1
            self.__bmp_data.append(bmp_data_row)
        if self.__hreversed : self.__bmp_data.reverse()
        # R, G, B 三个通道
        self.__R = []
        self.__G = []
        self.__B = []

        for row in range(self.__biHeight) :
            R_row = []
            G_row = []
            B_row = []
            for col in range(self.__biWidth) :
                B_row.append(self.__bmp_data[row][col][0])
                G_row.append(self.__bmp_data[row][col][1])
                R_row.append(self.__bmp_data[row][col][2])
            self.__B.append(B_row)
            self.__G.append(G_row)
            self.__R.append(R_row)
        
        del self.__stream
