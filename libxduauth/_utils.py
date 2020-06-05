import os
import sys


def parse_form_hidden_inputs(soup):
    return {
        item.get('name'): item.get('value', '')
        for item in soup.findAll('input', type='hidden')
    }


def try_get_vcode(img):
    from pytesseract import pytesseract
    img = _process_vcode(img)
    try:
        from importlib import resources
        with resources.path(__package__, 'ar.traineddata') as pkg_path:
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
        w, h = self.img.size
        self.img_arr = self.img.load()
        self.visited = set()
        sys.setrecursionlimit(w * h + 50)
        self.paint()

    DX = [1, 0, -1, 0]
    DY = [0, 1, 0, -1]

    def paint(self, value=255, x=0, y=0):
        if x < 0 or y < 0 or x >= self.img.size[0] or y >= self.img.size[1] or \
                (x, y) in self.visited:
            return False
        self.visited.add((x, y))
        for i in range(4):
            try:
                pixel = self.img_arr[x + self.DX[i], y + self.DY[i]]
            except IndexError:
                continue
            if abs(pixel - self.img_arr[x, y]) > 10:
                self.paint(255 - value, x + self.DX[i], y + self.DY[i])
            else:
                self.paint(value, x + self.DX[i], y + self.DY[i])
        self.img_arr[x, y] = value


def _process_vcode(img):
    p = Processor(img)
    return p.img
