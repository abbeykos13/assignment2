# using lab 03 to test the style checker 
class Caesar:
    def __init__(self, key: int):
        self._key = key  

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key: int):
        self._key = new_key

    def _shift_char(self, char: str, shift: int) -> str:
        if char.isalpha():
            base = ord('a')
            return chr(base + (ord(char.lower()) - base + shift) % 26)
        elif char.isdigit() or not char.isspace():  
            return chr((ord(char) + shift) % 256)
        return char  
    
    def encrypt(self, plaintext: str) -> str:
        return ''.join(self._shift_char(char, self._key) for char in plaintext)
    
    def decrypt(self, ciphertext: str) -> str:
        return ''.join(self._shift_char(char, -self._key) for char in ciphertext)


key = int(input("Enter shift key: "))
cipher = Caesar(key)

plaintext = input("Enter text to encrypt: ")
encrypted_text = cipher.encrypt(plaintext)
print("Encrypted:", encrypted_text)

decrypted_text = cipher.decrypt(encrypted_text)
print("Decrypted:", decrypted_text)
