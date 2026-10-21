"""
客户端: 无限和服务器发消息

功能:
    1. 从 input 读取内容, 反复发送给服务端
    2. 当输入的消息为 bye 时, 结束连接并退出

协议约定(客户端和服务端必须完全一致):
    - 编码: 统一使用 UTF-8, 否则中文会乱码
    - 分帧: 每条消息末尾加一个换行符 \\n 作为"消息结束"标记
            TCP 是字节流, 一次 recv 不保证收到完整的一条消息,
            加了分隔符后, 服务端才能可靠地按行切分出完整消息
"""
import socket

# ---------------- 配置项(两端保持一致) ----------------
HOST = "127.0.0.1"     # 服务端地址, 127.0.0.1 表示本机
PORT = 12345           # 服务端端口
ENCODING = "UTF-8"     # 统一的字符编码: 注意是 U-T-F-8, 不是 UFT-8
NEWLINE = b"\n"        # 消息分隔符, 用字节形式, 方便直接拼接发送
BUFFER_SIZE = 1024     # 单次接收缓冲区大小(服务端用)


def main() -> None:
    # with 语句: 无论正常结束还是中途抛异常, 离开时都会自动 client.close()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        # 连接服务端; 服务端没启动时会抛 ConnectionRefusedError
        client.connect((HOST, PORT))
        print(f"已连接到服务端 {HOST}:{PORT}")

        while True:
            # strip(): 去掉用户误输入的首尾空格/换行, 避免发出空白消息
            msg = input("请输入发送消息:  ").strip()

            # 空消息直接跳过, 不发送
            if not msg:
                print("消息不能为空, 请重新输入")
                continue

            # 先编码成字节, 再拼接分隔符: "你好" -> b"你好\n"
            data = msg.encode(ENCODING) + NEWLINE

            # sendall: 保证把所有字节都发出去
            # 比 send 可靠: send 可能只发出去一部分, 需要自己循环补发
            client.sendall(data)

            # bye 是约定的结束信号, 发给服务端后自己也要退出
            if msg == "bye":
                print("已发送 bye, 结束连接")
                break


if __name__ == "__main__":
    try:
        main()
    except ConnectionRefusedError:
        print(f"连接被拒绝: 请先启动服务端, 并确认 {HOST}:{PORT} 可以访问")
    except (ConnectionResetError, BrokenPipeError):
        print("连接已被服务端关闭, 发送失败")
    except KeyboardInterrupt:
        print("\n已手动中断")
