def LCSubStr(X, Y):
    
    m = len(X)
    n = len(Y)
    
    if m > n:
        m, n = n, m
        X, Y = Y, X
    
    i = j = 0
    while i < m:
        if X[i] == Y[j]:
            i += 1
            j += 1
        else:
            j += 1
        if j >= n:
            return i
    return m