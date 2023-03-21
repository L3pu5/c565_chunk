#
#  c565_chunked_image_raw, .c565 
#      By L3pu5, L3pu5_Hare
#  
#
#   c565_chunked_image_raw
#       Minimal image format for pre-chunked content.
#       .c565 is a RAW format with no checksum.
#       .c565 extension comes from original usecase: prechunking color565 images to be rendered faster with a buffer.
#
#   .c565 specifications.
#   Attribute       | Offset            | Length    | Preset
#                               HEADER
#   Magic numbers   | 0                 | 4         | C565
#   IMAGE_W_PX      | 4                 | 4         | 0000
#   IMAGE_H_PX      | 8                 | 4         | 0000
#   CHUNK_W_PX      | 12                | 4         | 0000
#   CHUNK_H_PX      | 16                | 4         | 0000
#   CHUNK_COL_CNT   | 20                | 2         | 00
#   CHUNK_SZ(byte)  | 22                | 10        | 0000 0000 00
#                                DATA
#   Chunk 0         | 32                | CHUNK_SZ  | 0*CHUNK_SZ
#   Chunk n         | 32+(n*Chunk_SZ)   | CHUNK_SZ  | 0*CHUNK_SZ
#
#   Chunks are, by definition, sections of X,Y grids to be drawn from
#   The top left to the bottom right
#   Chunks must be uniform, so they should be made so that they
#   divide the image plane uniformly and do not get drawn across
#   multiple buffers to the image device.

#   IMAGE_W_PX      --> Width of final image in pixels
#   IMAGE_H_PX      --> Height of final image in pixels
#   CHUNK_W_PX      --> Width of each chunk in pixels
#   CHUNK_H_PX      --> Height of each chunk in pixels
#   CHUNK_COL_CNT   --> Number of chunks per 'row' of the image.
#       .c565 is a landscape or 'row first' format. Images are
#       specified in rows
#   CHUNK_SZ        --> Size of each chunk in bytes.
#                   --> In c565 format, a pixel is 2 bytes.
#                   --> This can be reduced to 2*H*W from above.

#   A chunk contains image data, where it is written in square format
#   with the first byte being the first pixel in the top left
#   and the last byte being the bottom right, by rows.

#         [                   HEADER                    ] 
# Byte:   00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15
# Data:    C  5  6  5 [IMAGE_WID] [IMAGE_HEI] [CHUNK_WID]
#           
# Byte:   16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
# Data:   [CHUNK_HEI] [COL] [ CHUNK_SIZE_IN_BYTES       ]
#
from math import floor


class c565_chunk:
    width       = 0
    height      = 0
    chunk_x     = 0
    chunk_y     = 0
    buffer      = b""

    def __init__(self, x, y, width, height, buffer) -> None:
        self.x = x
        self.y = y

        self.width  = width
        self.height = height
        self.buffer = buffer

    def get_image_x(self) -> int:
        return self.x * self.width

    def get_image_y(self) -> int:
        return self.y * self.height
    
    def __str__(self) -> str:
        return f"Chunk {self.x}, {self.y} at {self.get_image_x()}, {self.get_image_y()}"


class c565_chunk_image:
    # By definition
    IMAGE_W_PX      = 0
    IMAGE_H_PX      = 0
    CHUNK_W_PX      = 0
    CHUNK_H_PX      = 0
    CHUNK_COL_CNT   = 0
    CHUNK_SZ        = 0
    DATA_OFFSET     = 32
    # Intermediates
    ACTIVE_FILE     = 0
    BUFFER          = b""
    # Calculted at ingestion
    CHUNK_COUNT     = 0
    CHUNK_ROW_CNT   = 0
    # State variables
    READY           = False
    INDEX           = 0
    EOF             = False

    def empty():
        return c565_chunk_image()
    
    # Writing to Files
    def accept_buffer(self, buffer: bytes):
        self.BUFFER = buffer

    # Baking for image c565 images
    # A buffer for writing in c565 format MUST be top-left 0,0 image data
    def set_baking_constraints_image(self, image_width: int, image_height: int):
        self.IMAGE_H_PX = image_height
        self.IMAGE_W_PX = image_width

    def bake_with_dimensions(self, chunk_width: int, chunk_height: int, chunk_size_in_bytes: int):
        #Bake chunk dimensions into the format if that are allowed.
        # The chunk dimensions MUST evenly divide the width and height
        if(self.IMAGE_W_PX % chunk_width != 0):
            raise Exception(f"Invalid width, does not divide the image. {chunk_width} requested against {self.IMAGE_W_PX}. Check dimensions")
        if(self.IMAGE_H_PX % chunk_height != 0):
            raise Exception(f"Invalid height, does not divide the image. {chunk_height} requested against {self.IMAGE_H_PX}. Check dimensions")

        self.CHUNK_H_PX = chunk_height
        self.CHUNK_W_PX = chunk_width
        
        self.CHUNK_COL_CNT = int(self.IMAGE_W_PX / chunk_width)
        self.CHUNK_ROW_CNT = int(self.IMAGE_H_PX / chunk_height)
        self.CHUNK_SZ = chunk_size_in_bytes
        # Chunk size is not calculated for the user, must be specified but should be 2*width*height


    def bake_to_file(self, path):
        f = open(path, "wb")
        #Header
        f.write(b"c565")
        #Image Height/Width
        f.write( (self.IMAGE_W_PX).to_bytes(4, "big"))
        f.write( (self.IMAGE_H_PX).to_bytes(4, "big"))
        # Chunk Height/Width
        f.write( (self.CHUNK_W_PX).to_bytes(4, "big"))
        f.write( (self.CHUNK_H_PX).to_bytes(4, "big"))
        # Chunk Row count
        f.write(  (self.CHUNK_ROW_CNT).to_bytes(2, "big"))
        # Chunk Size
        f.write( (self.CHUNK_SZ).to_bytes(10, "big"))
        # Buffer
        f.write(self.BUFFER)
        f.flush()
        f.close()

    def read_from_image_file(self, path):
        self.ACTIVE_FILE = open(path, "rb")
        if self.ACTIVE_FILE.read(4) != b"c565":
            print("File is not C565")
            return 11
        
        self.IMAGE_W_PX      = int.from_bytes(self.ACTIVE_FILE.read(4), "big")
        self.IMAGE_H_PX      = int.from_bytes(self.ACTIVE_FILE.read(4), "big")
        self.CHUNK_W_PX      = int.from_bytes(self.ACTIVE_FILE.read(4), "big")
        self.CHUNK_H_PX      = int.from_bytes(self.ACTIVE_FILE.read(4), "big")
        self.CHUNK_COL_CNT   = int.from_bytes(self.ACTIVE_FILE.read(2), "big")
        self.CHUNK_SZ        = int.from_bytes(self.ACTIVE_FILE.read(10), "big")
        self.calculate_fields_at_ingest()

    def print_index_position(self):
        print(f"{self.get_index_x()},{self.get_index_y()}")
        
    def get_index_x(self):
        return self.INDEX % self.CHUNK_COL_CNT
    
    def get_index_y(self):
        return floor(self.INDEX / self.CHUNK_COL_CNT)

    def iterate_with_c565chunks(self, lambda_function):
        self.index_seek(0)
        while self.EOF == False:
            lambda_function(self.next_chunk())

    def iterate_with_index_position(self, lambda_function):
        self.index_seek(0)
        while self.EOF == False:
            lambda_function((self.get_index_x(), self.get_index_y()), self.next())

    def iterate_with_index_position(self, lambda_function):
        self.index_seek(0)
        while self.EOF == False:
            lambda_function((self.get_index_x(), self.get_index_y()), self.next())

    def iterate(self, lambda_function):
        self.index_seek(0)
        while self.EOF == False:
            lambda_function(self.next())

    def next(self) -> bytes:
        if self.EOF == True:
            return None
        return self.read_chunk(self.INDEX)
    
    def next_chunk(self) -> c565_chunk:
        if self.EOF == True:
            return None
        return self.read_chunk_as_chunk(self.INDEX)      
    
    def calculate_fields_at_ingest(self):
        self.CHUNK_COUNT    = floor((self.IMAGE_W_PX * self.IMAGE_H_PX) / (self.CHUNK_W_PX * self.CHUNK_H_PX))
        self.CHUNK_ROW_CNT  = floor(self.CHUNK_COUNT / self.CHUNK_COL_CNT)

    def index_seek(self, index_offset: int):
        if index_offset >= self.CHUNK_COUNT:
            raise Exception(f"Invalid index address {index_offset} where chunk count is {self.CHUNK_COUNT}")
        self.INDEX = index_offset

    def read_chunk(self, chunk_offset: int) -> bytes:
        if(chunk_offset > self.CHUNK_COUNT - 1):
            raise Exception(f"Invalid chunk address {chunk_offset} where chunk count is {self.CHUNK_COUNT}")
        if chunk_offset == self.CHUNK_COUNT-1:
            self.EOF = True
        self.INDEX = chunk_offset + 1
        self.ACTIVE_FILE.seek(self.CHUNK_SZ*chunk_offset + self.DATA_OFFSET)
        return self.ACTIVE_FILE.read(self.CHUNK_SZ)
    
    def read_chunk_as_chunk(self, chunk_offset: int) -> c565_chunk:
        self.INDEX = chunk_offset
        return c565_chunk(self.get_index_x(), self.get_index_y(), self.CHUNK_H_PX, self.CHUNK_W_PX, self.read_chunk(chunk_offset))
    
    def __str__(self) -> str:
        return f"IMAGE :: {self.IMAGE_W_PX}x{self.IMAGE_H_PX} CHUNKS :: {self.CHUNK_W_PX}x{self.CHUNK_H_PX} BUFF :: {self.CHUNK_COL_CNT}"
