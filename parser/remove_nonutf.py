import os

# create file and combine all files in one
f2 = open("chatdata_with_nonutf.csv", "ab")
for file in os.listdir("data/"):
    with open("data/{}".format(file), "rb") as fp:
        first_line = True
        for line in fp:
            if first_line:
                first_line = False
                continue
            line = line.decode('utf-8', 'ignore').encode("utf-8")
            if line is not None or line != "":
                f2.write(line)

# Read the combined file
fi = open('chatdata_with_nonutf.csv', 'rb')
data = fi.read()
fi.close()

# Replace the non utf with utf chars
fo = open('chatdata.csv', 'wb')
fo.write(data.replace('\x00'.encode('utf-8'), bytes(''.encode('utf-8'))))
fo.close()
f2.close()

# Delete chatdata_with_nonutf.csv
os.remove('chatdata_with_nonutf.csv')
