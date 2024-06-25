from base64 import b64decode
from typing import Callable
from io import BytesIO
from PIL import Image


def _default_solver(data):
    Image.open(BytesIO(data)).show()
    return input('验证码: ')


def _rsbbs_solver(img):
    img = Image.open(BytesIO(img))
    img = img.convert('L')
    w, h = img.size
    img_arr = img.load()
    visited = set()
    q = []
    q.append((0, 0, 255))
    DX = [1, 0, -1, 0]
    DY = [0, 1, 0, -1]
    while q:
        x, y, value = q.pop()
        if x < 0 or y < 0 or x >= w or y >= h or \
                (x, y) in visited:
            continue
        visited.add((x, y))
        for i in range(4):
            try:
                pixel = img_arr[x + DX[i], y + DY[i]]
            except IndexError:
                continue
            if abs(pixel - img_arr[x, y]) > 5:
                q.append((x + DX[i], y + DY[i], 255 - value))
            else:
                q.append((x + DX[i], y + DY[i], value))
        img_arr[x, y] = value
    img.show()
    return input('验证码: ')


def _ids_solver(data):
    # data is {
    #     'bigImage': ..., # 背景图(base64)
    #     'smallImage': ..., # 滑块图(base64)
    #     'tagWidth": 93, # 无用, 恒93
    #     'yHeight': 0 # 无用, 恒0
    # }
    img = Image.open(BytesIO(b64decode(data['bigImage'])))
    img.show()

    # 输入背景图左侧到滑块目标位置左侧的宽度
    return int(input('滑块位移: ')) * 280 // img.width

_solvers = {
    'xk.xidian.edu.cn': _default_solver,
    'rsbbs.xidian.edu.cn': _rsbbs_solver,
    'ids.xidian.edu.cn': _ids_solver,
}

def get_solver(key) -> Callable:
    return _solvers.get(key, _default_solver)
