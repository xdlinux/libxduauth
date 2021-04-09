import os


def try_get_vcode(img):
    from pytesseract import pytesseract
    img = _process_vcode(img)
    try:
        try:
            from importlib.resources import path
        except ImportError:
            from importlib_resources import path
        with path(__package__, os.path.join('assets', 'ar.traineddata')) as pkg_path:
            vcode = pytesseract.image_to_string(
                img, lang='ar',
                config="--psm 7 --tessdata-dir " +
                       os.path.dirname(pkg_path)
            )
    except:
        vcode = pytesseract.image_to_string(
            img, lang='eng', config="--psm 7")
    return vcode


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
