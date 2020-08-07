from base64 import b32encode,b32decode
from PyQt5 import *
def Cipher(text, key):
      result = "";
      ptr = 0;
      for char in text:
            result = result + chr(ord(char) ^ ord(key[ptr]));
            ptr = ptr + 1;
            if ptr == len(key):
                  ptr = 0;
      return bytes(result,"utf-8")
def load(self,fobject):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Enter File Password - MSOPad', 'Enter Decryption key')
        if text == "":
                key = "Zencode MSOPad"
        else:
                key = text
        return Cipher(bytes.fromhex(fobject.read()).decode(),text).decode()
def dump(self,text,fobject):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Enter File Password - MSOPad', 'Enter Encryption key')
        if text == "":
                key = "Zencode MSOPad"
        else:
                key = text
        outn = str(Cipher(text,key).hex())
        print(outn)
        fobject.write(outn)
def dump_no_message(self,text,fobject):
        outn = str(Cipher(text,key).hex())
        print(outn)
        fobject.write(outn)
