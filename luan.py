with open("tldnames.txt", "r") as file:
    tlds = [l.strip() for l in file]

def isTLD(str):
    return str in tlds

def validString(str):
    i = 0
    length = len(str)
    if length == 0:
        return False

    while i < length:
        letter = str[i]

        if letter == "@":
            # print(letter)
            return False

        if i == 0 and letter == ".":
            # print(letter)
            return False
        
        if (not letter.isalnum() and letter not in ["!", "#", "$", "%", "&", "'", "*", "+", "-", "/", "=", "?", "^", "_", "`", "{", "|", "}", "~", "."]):
            # print(letter)
            return False

        i += 1

    return True

def idnConversion(str):
    domain = str.encode("idna").decode("ascii")
    return domain

def is_valid(email):
    local, domain = email.split("@")

    if not validString(local):
        return False

    # domain
    parts = domain.split(".")
    for i, p in enumerate(parts):
        if not validString(p):
            return False
        
    if not isTLD(parts[-1].upper()):
        return False

    return True

# domain = email[i:]

print(is_valid("a@comp.com"))
# print("%".isalnum())