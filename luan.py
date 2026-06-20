def validString(str):
    i = 0
    length = len(str)

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


def is_valid(email):
    local, domain = email.split("@")

    if not validString(local):
        return False

    # domain
    return True

# domain = email[i:]

print(is_valid("a@comp.com"))
# print("%".isalnum())