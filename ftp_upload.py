import ftplib, os

ftp_host = os.getenv("FTP_HOST")
ftp_user = os.getenv("FTP_USER")
ftp_pass = os.getenv("FTP_PASS")

def upload_dir(local_dir, ftp_dir, ftp):
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        ftp_path = f"{ftp_dir}/{item}"

        if os.path.isdir(local_path):
            try:
                ftp.mkd(ftp_path)
            except:
                pass
            upload_dir(local_path, ftp_path, ftp)
        else:
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {ftp_path}", f)
                print(f"[UPLOADED] {ftp_path}")

ftp = ftplib.FTP(ftp_host)
ftp.login(ftp_user, ftp_pass)
ftp.cwd("public_html")  # Hostinger 默认目录

upload_dir("website", ".", ftp)
upload_dir("output", ".", ftp)

ftp.quit()

