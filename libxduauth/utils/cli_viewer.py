from PIL.ImageShow import Viewer, register as register_pil_imshow
from PIL import Image


def _image_to_ascii(img, size=(80, 16), invert_pallete=True):
    # convert image to ascii art for cli view
    # given char dimension 24*16, optimal sizes are
    # (80, 16) for xk, (80, 21) for rsbbs
    if invert_pallete:
        chs = '@&%QWNM0gB$#DR8mHXKAUbGOpV4d9h6Pkqwaxoenut1ivsz/*cr!+<>;=^:\'-.` '
    else:
        chs = ' `.-\':^=;><+!rc*/zsvi1tuneoxawqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@'
    w, h = size
    img.load()
    im = img.im.convert('L').resize((w, h))
    return '\n'.join(''.join(
        chs[im[i] // 4] for i in range(y, y + w)
    ) for y in range(0, w * h, w))


class _CliViewer(Viewer):
    def show(self, image: Image.Image, **options: Image.Any) -> int:
        print(_image_to_ascii(image))
        # always attempt other viewers
        return False

def register():
    register_pil_imshow(_CliViewer, 0)
