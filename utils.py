def wprint(s, fd=None):
    if(fd is not None): fd.write(s + '\n')
    print(s)
    return 