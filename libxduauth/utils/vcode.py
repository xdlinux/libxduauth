from base64 import b64decode
from typing import Callable
from io import BytesIO
from PIL import Image


def _default_solver(data):
    Image.open(BytesIO(data)).show()
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
    'ids.xidian.edu.cn': _ids_solver,
}


def get_solver(key) -> Callable:
    return _solvers.get(key, _default_solver)
