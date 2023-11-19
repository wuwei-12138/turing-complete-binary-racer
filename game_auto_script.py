"""游戏《图灵测试》快速二进制计算关卡成就脚本

脚本处理步骤如下：
1. pyautogui在指定位置每隔半秒截图一次
2. cnorc自动识别图片中的数字
3. 计算数字中的二进制
4. pyatuogui模拟键盘和鼠标输入进行游戏操作

前置安装：
pip install pyautogui cnocr[ort-cpu]

使用方法：
1. 游戏以窗口化模式运行，打开相关关卡，界面没有经过wasd移动或缩放
2. 运行脚本，带控制栏出现“程序正式开始”字样切回游戏界面
3. 点击游戏画面中的开始

可能遇见的问题
1. cnorc的识别率不是很高, ‘勺’和‘女’字可能误识别位'9'
调整截图的大小，使其包含完整字或半个字，前者会提高准确率，后者不会去识别
2. 脚本出现死循环
将鼠标移动到主屏幕的左上角，可以中断程序运行
"""

import time
import pyautogui
from PIL import Image
from cnocr import CnOcr

# 超时时间，秒
TIME_OUT = 130
# 间隔时间，秒
TIME_SPLIT = 0.5
# 最大错误次数
MAX_MISS = 5
# 截图起点位置和大小
SCREEN_SHOT_POTION = (880, 490, 127, 50)
# 提交按钮位置
SUBMIT_POSTION = (950, 980)
# 游戏中空白位置
SPACE_POSTION = (930, 800)

# 启用中断，将鼠标移动到左上角会抛中断停止程序，防止pyautogui失控导致无法操作电脑
pyautogui.FAILSAFE = True


def screen_copy(pos=SCREEN_SHOT_POTION) -> Image:
    """在指定起始位置截图"""
    img = pyautogui.screenshot(region=pos)
    return img


def mouse_postion():
    """调试函数，打印鼠标位置

    如果不清楚截图和按钮位置，可以使用该函数获取基础信息"""
    print("press ctrl-c to quit")
    try:
        while True:
            x, y = pyautogui.position()
            print("({}, {})".format(x, y))
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n")


def orc_scan(orc_obj: CnOcr, image: Image) -> int:
    """orc扫描图片, 数字表示识别成功, None表示识别失败"""
    out = orc_obj.ocr(image)
    # 图片中没有文字
    if not out:
        image.save("./game_screen/None.jpeg")
        return None
    # 将多行文字统一处理
    text = ""
    for item in out:
        text += item["text"]
    # 游戏失败画面中的文字，确定已失败
    # 注意，不要用‘备好了’为关键字，‘了’任意被误识别为7影响准确率
    if "备好" in text:
        return None
    num = ""
    try:
        flag = False  # 表示数是否连续，截图中半个汉字或部首容易被误识别为数字
        for item in text:
            if str.isdigit(item):
                num += item
                flag = True
            elif flag:
                break
        # 一些实在无法调整的误识别，通过硬编码方式解决吧
        hard_code = ["109", "129"]
        for item in hard_code:
            if item in num:
                num = item
                break
        num = int(num)
        # # 调试用代码，如果出现输入错误，可以启用该代码，查看截图内容和对应识别结果
        # image.save(
        #     "./game_screen/N-{}-{}.jpeg".format(time.strftime("%Y%m%d%H%M%S"), num)
        # )
    except Exception:
        image.save("./game_screen/E{}.jpeg".format(out[0]["text"]))
        print(out)
        return None
    return num


def cal_num_bit(num: int) -> str:
    """计算数字对应二进制"""
    # 位补齐
    return "{:>08}".format(bin(num)[2:])


def get_contrl_str(input: str) -> list[str]:
    """根据数字生成按键操作字符串"""
    out = []
    for seq, item in enumerate(input):
        if item == "1":
            out.append(str(seq + 1))
    return out


def game_contrl(input: list[str]):
    """游戏按键操作"""
    pyautogui.click(SPACE_POSTION)  # 点击一下游戏画面，确保后续键盘输入完整
    pyautogui.press(input, interval="0.05")
    pyautogui.moveTo(SUBMIT_POSTION)
    pyautogui.click()


def main_work():
    """主运行事件"""

    print("程序正式开始")
    time.sleep(2)

    st_fl = time.time()
    miss_cnt = 0

    # 指定识别的字符集，减小误识别概率
    # 小写‘o’，大写‘O’和数字‘0’容易误识别
    # 汉字‘了’和数字‘7’容易误识别
    ocr_obj = CnOcr(cand_alphabet="勺的如准备好吗女0123456789")

    while miss_cnt < MAX_MISS:
        # 超时中断
        nw_fl = time.time()
        if nw_fl - st_fl > TIME_OUT:
            break

        img_obj = screen_copy()
        num_obj = orc_scan(ocr_obj, img_obj)
        if num_obj is None:
            time.sleep(TIME_SPLIT)
            print("miss")
            miss_cnt += 1
            continue
        # 根据数字生成操作字符串
        bin_obj = cal_num_bit(num_obj)
        ctl_obj = get_contrl_str(bin_obj)
        # 将操作字符串输入到游戏
        game_contrl(ctl_obj)

        ed_fl = time.time()
        print("{0:>3}耗时{1:.2f}秒，操作".format(num_obj, ed_fl - nw_fl), end="")
        print(ctl_obj)
        time.sleep(TIME_SPLIT)  # 给游戏刷新时间


if __name__ == "__main__":
    # mouse_postion()
    main_work()
