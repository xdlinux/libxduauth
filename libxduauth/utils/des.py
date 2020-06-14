kmap = [13, 16, 10, 23, 0, 4, 2, 27, 14, 5, 20, 9, 22, 18, 11, 3, 25, 7, 15, 6, 26, 19, 12, 1, 40,
        51, 30, 36, 46, 54, 29, 39, 50, 44, 32, 47, 43, 48, 38, 55, 33, 52, 45, 41, 49, 35, 28, 31]
pPermute = [15, 6, 19, 20, 28, 11, 27, 16, 0, 14, 22, 25, 4, 17, 30, 9,
            1, 7, 23, 13, 31, 26, 2, 8, 18, 12, 29, 5, 21, 10, 3, 24]
finalPermute = [39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53,
                21, 61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2,
                42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25, 32, 0, 40, 8, 48, 16, 56, 24]


def xor(byteOne, byteTwo):
    leng = len(byteOne)
    xorByte = [0] * leng
    for i in range(leng):
        xorByte[i] = byteOne[i] ^ byteTwo[i]
    return xorByte


def expandPermute(rightData):
    return [
        rightData[(i * 4 + j + 31) % 32]
        for i in range(8) for j in range(6)
    ]


sbox = [
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]


def sBoxPermute(expandByte):
    sBoxByte = ""
    for m in range(8):
        i = expandByte[m * 6 + 0] * 2 + expandByte[m * 6 + 5]
        j = expandByte[m * 6 + 1] * 2 * 2 * 2 + expandByte[m * 6 + 2] * \
            2 * 2 + expandByte[m * 6 + 3] * 2 + expandByte[m * 6 + 4]
        sBoxByte += f'{sbox[m][i][j]:04b}'
    return [int(c) for c in sBoxByte]


def generateKeys(keyByte):
    key = [0] * 56
    keys = [[0] * 48 for i in range(16)]
    loop = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
    for i in range(7):
        k = 7
        for j in range(8):
            key[i * 8 + j] = keyByte[8 * k + i]
            k -= 1
    for i in range(16):
        for j in range(loop[i]):
            tempLeft = key[0]
            tempRight = key[28]
            for k in range(27):
                key[k] = key[k + 1]
                key[28 + k] = key[29 + k]

            key[27] = tempLeft
            key[55] = tempRight
        for m in range(48):
            keys[i][m] = key[kmap[m]]
    return keys


def enc(data, keyByte):
    keys = generateKeys(keyByte)
    ipByte = [0] * 64
    for i in range(4):
        k = 0
        for j in range(7, -1, -1):
            ipByte[i * 8 + k] = data[j * 8 + i * 2 + 1]
            ipByte[i * 8 + k + 32] = data[j * 8 + i * 2]
            k += 1
    ipLeft = [0] * 32
    ipRight = [0] * 32
    tempLeft = [0] * 32

    for k in range(32):
        ipLeft[k] = ipByte[k]
        ipRight[k] = ipByte[32 + k]
    for i in range(16):
        for j in range(32):
            tempLeft[j] = ipLeft[j]
            ipLeft[j] = ipRight[j]
        key = [0] * 48
        for m in range(48):
            key[m] = keys[i][m]
        tp = sBoxPermute(xor(expandPermute(ipRight), key))
        tempRight = xor(
            [tp[i] for i in pPermute],
            tempLeft
        )
        for n in range(32):
            ipRight[n] = tempRight[n]
    finalData = [0] * 64
    for i in range(32):
        finalData[i] = ipRight[i]
        finalData[32 + i] = ipLeft[i]

    return [finalData[i] for i in finalPermute]


def encrypt(s, keys):
    result = ''
    for group in [s[i:i + 4] for i in range(0, len(s), 4)]:
        group = [int(i) for i in ''.join(
            [f'{ord(i):016b}' for i in group.ljust(4, '\0')])]
        for k in keys:
            for i in [k[i:i + 4] for i in range(0, len(k), 4)]:
                group = enc(
                    group,
                    [int(i) for i in ''.join(
                        [f'{ord(i):016b}' for i in i.ljust(4, '\0')])]
                )
        result += f'{int("".join([str(i) for i in group]), 2):X}'
    return result
