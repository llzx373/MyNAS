# encoding=utf8

from flask import Blueprint
from qbittorrent import Client
from config import qbittorrent_url,qbittorrent_username,qbittorrent_password
from util import json_return
qbtbp=Blueprint('qbt',__name__)

'''
这里主要作为bt任务查看，新增，删除三个作用
'''

@qbtbp.route("/list")
def list_torrents():
    bt=Client(qbittorrent_url)
    bt.login(qbittorrent_username,qbittorrent_password)
    return json_return(
        bt.torrents()
    )