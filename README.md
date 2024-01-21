# c565_chunk

  c565_chunked_image_raw, .c565 
      By L3pu5, L3pu5_Hare
  

   c565_chunked_image_raw
       Minimal image format for pre-chunked content.
       .c565 is a RAW format with no checksum.
       .c565 extension comes from original usecase: prechunking color565 images to be rendered faster with a buffer.

   .c565 specifications.
   
   |Attribute       | Offset            | Length    | Preset|
   | --  | -- | -- |  
   Magic numbers   | 0                 | 4         | C565
   IMAGE_W_PX      | 4                 | 4         | 0000
   IMAGE_H_PX      | 8                 | 4         | 0000
   CHUNK_W_PX      | 12                | 4         | 0000
   CHUNK_H_PX      | 16                | 4         | 0000
   CHUNK_COL_CNT   | 20                | 2         | 00
   CHUNK_SZ(byte)  | 22                | 10        | 0000 0000 00            
   Chunk 0         | 32                | CHUNK_SZ  | 0*CHUNK_SZ
   Chunk n         | 32+(n\*Chunk_SZ)   | CHUNK_SZ | 0*CHUNK_SZ

   Chunks are, by definition, sections of X,Y grids to be drawn from
   The top left to the bottom right
   Chunks must be uniform, so they should be made so that they
   divide the image plane uniformly and do not get drawn across
   multiple buffers to the image device.
   IMAGE_W_PX      --> Width of final image in pixels
   IMAGE_H_PX      --> Height of final image in pixels
   CHUNK_W_PX      --> Width of each chunk in pixels
   CHUNK_H_PX      --> Height of each chunk in pixels
   CHUNK_COL_CNT   --> Number of chunks per 'row' of the image.
       .c565 is a landscape or 'row first' format. Images are
       specified in rows
   CHUNK_SZ        --> Size of each chunk in bytes.
                   --> In c565 format, a pixel is 2 bytes.
                   --> This can be reduced to 2\*H\*W from above.
   A chunk contains image data, where it is written in square format
   with the first byte being the first pixel in the top left
   and the last byte being the bottom right, by rows.
         [                   HEADER                    ] 
 Byte:   00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15
 Data:    C  5  6  5 \[IMAGE_WID] \[IMAGE_HEI] \[CHUNK_WID]
           
 Byte:   16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
 Data:   \[CHUNK_HEI] \[COL] [ CHUNK_SIZE_IN_BYTES       ]
