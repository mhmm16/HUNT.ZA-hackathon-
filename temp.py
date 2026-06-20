temp = "com"
domain = temp.encode('idna').decode("ascii")
print(domain)