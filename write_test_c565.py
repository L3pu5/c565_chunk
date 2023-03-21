f = open("testfile.c565", "wb")
f.write(b"c565")
#Image Height/Width
f.write( (60).to_bytes(4, "big"))
f.write( (24).to_bytes(4, "big"))
# Chunk Height/Width
f.write( (12).to_bytes(4, "big") )
f.write((12).to_bytes(4, "big"))
# Chunk Row count
f.write((5).to_bytes(2, "big"))
# Buffer Size
f.write((48).to_bytes(10, "big"))
for i in range(10):
    f.write( (0x69).to_bytes(2, "big") * 48)

f.flush()
f.close()