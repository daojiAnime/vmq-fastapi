# 写一个二维码解析器，可以解析二维码中的文本信息

from io import BytesIO

from PIL import Image

# 使用 pyzbar 库解析二维码
from pyzbar.pyzbar import Decoded, decode  # type: ignore


def parse_qrcode(qrcode_path: BytesIO) -> str:
    """
    解析二维码中的文本信息
    """

    # 将 BytesIO 转换为 PIL 图像
    image = Image.open(qrcode_path)
    # 解析二维码
    decoded_objects: list[Decoded] = decode(image)
    # 返回解析结果
    return decoded_objects[0].data.decode("utf-8")  # type: ignore


def main() -> None:
    # 读取二维码图片
    with open("WechatIMG1171.jpg", "rb") as f:
        qrcode_path = BytesIO(f.read())
    # 解析二维码
    text = parse_qrcode(qrcode_path)
    print(text)
