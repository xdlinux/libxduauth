class Processor:
    def __init__(self, img):
        self.img = img.convert('L')
        self.img_arr = self.img.load()
        self.paint()

    DX = [1, 0, -1, 0]
    DY = [0, 1, 0, -1]

    def paint(self):
        w, h = self.img.size
        visited = set()
        q = []
        q.append((0, 0, 255))
        while q:
            x, y, value = q.pop()
            if x < 0 or y < 0 or x >= w or y >= h or \
                    (x, y) in visited:
                continue
            visited.add((x, y))
            for i in range(4):
                try:
                    pixel = self.img_arr[x + self.DX[i], y + self.DY[i]]
                except IndexError:
                    continue
                if abs(pixel - self.img_arr[x, y]) > 5:
                    q.append((x + self.DX[i], y + self.DY[i], 255 - value))
                else:
                    q.append((x + self.DX[i], y + self.DY[i], value))
            self.img_arr[x, y] = value


def _process_vcode(img):
    p = Processor(img)
    return p.img
