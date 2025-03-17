import os
from ftplib import FTP

def load_file_to_ftp(file_path, ftp_host, ftp_user, ftp_password):
    ftp = FTP(ftp_host)
    ftp.login(user=ftp_user, passwd=ftp_password)
    with open(file_path, 'rb') as xml_file:
        ftp.storbinary(f"STOR {os.path.basename(file_path)}", xml_file)
    ftp.quit()