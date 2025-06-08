import ftplib
import os

# 读取环境变量
ftp_host = os.getenv("FTP_HOST")
ftp_user = os.getenv("FTP_USER")
ftp_pass = os.getenv("FTP_PASS")

if not all([ftp_host, ftp_user, ftp_pass]):
    print("错误：请先设置环境变量 FTP_HOST、FTP_USER、FTP_PASS")
    exit(1)

def upload_dir(local_dir, ftp_dir, ftp):
    """
    递归上传 local_dir 目录及子目录文件到 FTP 服务器 ftp_dir 路径。
    """
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        ftp_path = f"{ftp_dir}/{item}" if ftp_dir != '.' else item

        if os.path.isdir(local_path):
            try:
                ftp.mkd(ftp_path)
                print(f"[MKDIR] 创建目录 {ftp_path}")
            except ftplib.error_perm as e:
                # 目录已存在，忽略错误
                if '550' in str(e):
                    pass
                else:
                    print(f"[WARN] 创建目录异常: {e}")
            upload_dir(local_path, ftp_path, ftp)
        else:
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {ftp_path}", f)
                print(f"[UPLOADED] 上传文件 {ftp_path}")

def main():
    try:
        ftp = ftplib.FTP(ftp_host, timeout=30)
        ftp.login(ftp_user, ftp_pass)
        print(f"已连接FTP服务器：{ftp_host}")

        # 切换到网站根目录，根据你的 Hostinger 设置调整路径
        ftp.cwd("domains/cloakaccess.com/public_html")
        print("切换到 FTP 目录：/domains/cloakaccess.com/public_html")

        # 上传 website/ 文件夹内容
        local_website = "website"
        if not os.path.exists(local_website):
            print(f"本地文件夹 '{local_website}' 不存在，请确认路径")
            return
        upload_dir(local_website, ".", ftp)

        # 上传 output/ 文件夹内容（nodes.json）
        local_output = "output"
        if not os.path.exists(local_output):
            print(f"本地文件夹 '{local_output}' 不存在，请确认路径")
            return
        upload_dir(local_output, ".", ftp)

        ftp.quit()
        print("上传完成，FTP连接关闭。")
    except Exception as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    main()
