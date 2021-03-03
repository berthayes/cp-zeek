import boto3
from configparser import ConfigParser
import os

config_file = './yak_shaving.conf'
cfg = ConfigParser()
cfg.read(config_file)

download = cfg.get('s3pcap', 'download_pcap')
if download == 'True':
    print("download_pcap = True in config")
    s3bucket = cfg.get('s3pcap', 's3_bucket_name')
    s3object = cfg.get('s3pcap', 's3_object_name')
    print("Renaming existing zeek_streamer.pcap file")
    os.rename('../pcaps/zeek_streamer.pcap', '../pcaps/zeek_streamer.pcap.bak')
    print("Downloading pcap file from " + s3bucket + "/" + s3object)

    s3 = boto3.client('s3')
    s3.download_file(s3bucket, s3object, '../pcaps/zeek_streamer.pcap')

elif cfg.get('s3pcap', 'download_pcap') == 'False':
    print("download_pcap = False in config")
    print("skipping pcap download from S3")
