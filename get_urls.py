def open_file(fname):
    routok = []
    csak_route = []
    with open(fname, encoding="utf8") as f:
        file = f.readlines()
        for sor in file:
            if "@app.route" in sor:
                if "methods" in sor:
                    routok.append(sor[12:-2])
                    if "['POST', 'GET']" in sor:
                        csak_route.append(sor[12:-28])    
                    else:
                        csak_route.append(sor[12:-21])
                else:
                    routok.append(sor[12:-3])
    
    for i in routok:
        if "methods" in i:
            continue
        csak_route.append(i)
    
    
    
    return csak_route
        
print(open_file("main.py"))

if __name__ == "__main__":
    open_file("main.py")