import string

BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

def encode(num: int) -> str:
    """Encodes a positive integer to Base62."""
    if num < 0:
        raise ValueError("Number must be non-negative.")
    if num == 0:
        return BASE62_ALPHABET[0]
    
    encoded = []
    while num > 0:
        num, rem = divmod(num, 62)
        encoded.append(BASE62_ALPHABET[rem])
    
    return ''.join(reversed(encoded))

def decode(s: str) -> int:
    """Decodes a Base62 string back to an integer."""
    if not s:
        raise ValueError("String cannot be empty.")
    num = 0
    for char in s:
        if char not in BASE62_ALPHABET:
            raise ValueError(f"Invalid character in Base62 string: {char}")
        num = num * 62 + BASE62_ALPHABET.index(char)
    return num
