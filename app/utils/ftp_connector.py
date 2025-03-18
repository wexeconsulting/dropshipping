import os
from ftplib import FTP_TLS
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_file_to_ftp(file_path, ftp_host, ftp_user, ftp_password):
    def calculate_md5(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_remote_md5(ftp, remote_file_path):
        hash_md5 = hashlib.md5()
        ftp.retrbinary(f"RETR {remote_file_path}", hash_md5.update)
        return hash_md5.hexdigest()

    attempt = 0
    max_attempts = 5
    while attempt < max_attempts:
        logger.info(f"Attempt {attempt + 1} of {max_attempts}")

        logger.info(f"Calculating MD5 for local file: {file_path}")
        local_md5 = calculate_md5(file_path)
        logger.info(f"Local MD5: {local_md5}")

        ftp = FTP_TLS(ftp_host)
        ftp.prot_p()
        ftp.login(user=ftp_user, passwd=ftp_password)
        logger.info(f"Connected to FTP server: {ftp_host}")

        with open(file_path, 'rb') as xml_file:
            logger.info(f"Uploading file to FTP: {file_path}")
            ftp.storbinary(f"STOR {os.path.basename(file_path)}", xml_file, 1024)
            logger.info(f"File uploaded: {file_path}")

        logger.info(f"Calculating MD5 for remote file: {os.path.basename(file_path)}")
        remote_md5 = get_remote_md5(ftp, os.path.basename(file_path))
        logger.info(f"Remote MD5: {remote_md5}")

        ftp.quit()
        logger.info("FTP connection closed")

        if local_md5 == remote_md5:
            logger.info("File transfer successful: checksums match")
            break
        else:
            logger.error("File transfer failed: checksum mismatch")
            attempt += 1
            if attempt == max_attempts:
                raise ValueError("File transfer failed after multiple attempts: checksum mismatch")
            logger.info("Retrying file transfer...")