import ftplib
import os
import sys

ftp_host = os.getenv("FTP_HOST")
ftp_user = os.getenv("FTP_USER")
ftp_pass = os.getenv("FTP_PASS")

if not all([ftp_host, ftp_user, ftp_pass]):
    print("错误：请先设置环境变量 FTP_HOST、FTP_USER、FTP_PASS")
    sys.exit(1)

LOCAL_UPLOAD_DIR = "website"
FTP_BASE_DIR = "domains/cloakaccess.com/public_html"

def upload_dir(local_dir, ftp_dir, ftp):
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        ftp_path = f"{ftp_dir}/{item}" if ftp_dir != '.' else item

        if os.path.isdir(local_path):
            try:
                ftp.mkd(ftp_path)
                print(f"[MKDIR] 创建目录 {ftp_path}")
            except ftplib.error_perm as e:
                if '550' in str(e):
                    # 目录已存在，忽略
                    pass
                else:
                    print(f"[WARN] 创建目录异常: {e}")
            upload_dir(local_path, ftp_path, ftp)
        else:
            try:
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR {ftp_path}", f)
                    print(f"[UPLOADED] 上传文件 {ftp_path}")
            except Exception as e:
                print(f"[ERROR] 上传文件 {ftp_path} 失败: {e}")

def main():
    try:
        ftp = ftplib.FTP(ftp_host, timeout=30)
        ftp.login(ftp_user, ftp_pass)
        print(f"已连接FTP服务器：{ftp_host}")

        ftp.cwd(FTP_BASE_DIR)
        print(f"切换到 FTP 目录：{FTP_BASE_DIR}")

        if not os.path.exists(LOCAL_UPLOAD_DIR):
            print(f"本地文件夹 '{LOCAL_UPLOAD_DIR}' 不存在，请确认路径")
            return

        upload_dir(LOCAL_UPLOAD_DIR, ".", ftp)

        ftp.quit()
        print("上传完成，FTP连接关闭。")
    except Exception as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    main()
