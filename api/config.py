# encoding=utf8

pg_conninfo = "host=192.168.1.21 port=15432 user=app password=Qwer1234 dbname=mynas"
ignore_file = ['.DS_Store', 'Thumbs.db']
ignore_dir = ['@eaDir', '__gsdata__']
PHOTO_BUF_SIZE = 1024000
PHOTO_CATCH = "/tmp/mynas/"
support_file = {
    'photo': ",".join(["jpg", 'png', 'bmp', 'jpeg', 'gif']),
    'novel': ",".join(["txt", 'md']),
    'music': ",".join(["mp3", 'wma']),
    'video': ",".join(['mp4', 'avi', 'mkv', 'webm', 'flv', 'mov']),
}
__file_ex2type = {
    'mp4': "video", 'avi': "video", 'mkv': "video", 'webm': "video", 'flv': "video", 'mov': "video",
    "jpg":'photo', 'png':'photo', 'bmp':'photo', 'jpeg':'photo', 'gif':'photo','mp3':'music','wma':'music'
}


def file_ex2type(filename):
    ptype = filename.split('.')[-1].lower()
    return __file_ex2type.get(ptype,'file')

ffmpeg_path = "/usr/bin/ffmpeg"
ffprobe_path = "/usr/bin/ffprobe"

# mac:h264_videotoolbox nvidia:h264_nvenc 无显卡：libx264 intel：h264_qsv
ffmpeg_codec="h264_nvenc"
redis_conn = {
    'host': '127.0.0.1',
    'port': 6379
}
