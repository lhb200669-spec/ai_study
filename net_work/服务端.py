"""
服务端: 可以接收任意数量的客户端, 但同一时刻只服务一个客户端

工作流程:
    1. 启动后阻塞在 accept(), 等待客户端连接
    2. 连上后不断 recv(), 打印收到的消息
    3. 收到 bye 或客户端断开, 关闭该连接, 回到 accept() 等下一位

协议约定(必须和客户端一致):
    - 编码: UTF-8
    - 分帧: 每条消息以 \\n 结尾, 服务端攒够一行再解码
"""
import socket
import multiprocessing as mp

# ---------------- 配置项(两端保持一致) ----------------
HOST = "127.0.0.1"     # 监听地址
PORT = 12345           # 监听端口
ENCODING = "UTF-8"     # 统一的字符编码: 注意是 U-T-F-8
NEWLINE = b"\n"        # 消息分隔符(字节形式)
BUFFER_SIZE = 1024     # 单次 recv 最多接收的字节数


def handle_client(client: socket.socket, client_info: tuple) -> None:
    """服务一个客户端, 直到它发来 bye 或主动断开连接."""
    # 字节缓冲区: 保存"还没凑够一整行"的数据
    # 用 bytes 而不是 str, 因为半个汉字被解码会变成乱码
    buffer = b""

    while True:
        data = client.recv(BUFFER_SIZE)
        # recv 返回空字节串 b"" 表示对端已关闭连接(不算异常)
        # 如果不判断, 循环会空转, 疯狂打印空消息
        if not data:
            print(f"客户端{client_info} 已断开")
            return

        buffer += data

        # 一次 recv 可能只收到半条消息, 也可能一次收到好几条
        # 所以循环把缓冲区里所有完整的"行"都处理掉
        while NEWLINE in buffer:
            line, buffer = buffer.split(NEWLINE, 1)

            # 只对完整的一行字节做解码, 避免多字节字符被切开
            text = line.decode(ENCODING)

            print(f"收到客户端{client_info}的消息: {text}")

            # 收到 bye: 结束本次会话, 返回后由外层 with 关闭连接
            if text == "bye":
                print(f"客户端{client_info} 发送 bye, 关闭连接")
                return



def main() -> None:
    # with: 退出时自动关闭监听套接字, 释放端口
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # 允许端口复用: 服务端重启后不会报
        # OSError: [WinError 10048] 通常每个套接字地址只允许使用一次
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((HOST, PORT))
        server.listen()
        print(f"服务端已启动, 正在 {HOST}:{PORT} 监听...")

        # 外层循环: 反复接受新客户端, 一次只服务一个
        while True:
            client, client_info = server.accept()
            print(f"客户端{client_info} 已连接")
            # with: 无论处理成功还是出错, 离开时都会 client.close()
            with client:
                mp.Process(target=handle_client, args=(client, client_info)).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n服务端已手动关闭")
    except OSError as exc:
        print(f"服务端启动失败: {exc}")
