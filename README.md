# ref to [xidian-scripts](https://github.com/xdlinux/xidian-scripts)

# libxduauth

本仓库用于辅助西安电子科技大学各种服务网站**不用于自动化测试的**爬虫的编写<br>
涉及到验证码时**需要手动进行输入**

## 使用方式

```python
from libxduauth import *
ses = EhallSession('用户名', '密码')
# 进行后续请求
```

## 支持的平台

class         | domain                                | description
:------------ | :------------------------------------ | :--------------
EhallSession  | <http://ehall.xidian.edu.cn>          | 一站式服务中心，继承自统一认证
EnergySession | <http://10.168.55.50:8088>            | 水表/电表查询
IDSSession    | <http://ids.xidian.edu.cn/authserver> | 统一认证
RSBBSSession  | <http://rsbbs.xidian.edu.cn>          | 睿思论坛（外网）
WXSession     |                                       |
XKSession     | <http://xk.xidian.edu.cn>             | 选课系统
ZFWSession    | <https://zfw.xidian.edu.cn>           | 校园网流量购买/查询

## 声明

本项目无意增加服务端压力。<br>
如果网站本身正确实现了验证码机制，`libxduauth`不会试图对其进行绕过。<br>
默认情况下`libxduauth`也没有进行请求的伪装，非常容易识别（`UA: python-requests/<version>`）
