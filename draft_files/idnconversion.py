temp = "政府"
domain = temp.encode('idna').decode("ascii")
print(domain)

def idnConversion(str):
    print(str)
    domain = str.encode("idna").decode("ascii")
    print(domain)
    return domain


idnConversion("政府")