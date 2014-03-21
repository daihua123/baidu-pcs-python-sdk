#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import os
# import pdb
# from PIL import Image
# from StringIO import StringIO

from baidupcs import PCS
from .utils import content_md5, content_crc32, slice_md5

logging.basicConfig(level=logging.WARN,
                    format='\n%(funcName)s - %(lineno)d\n%(message)s')
logger = logging.getLogger(__name__)

access_token = '23.a4c9142268c190e82bff02905fb79b98.2592000.1397954722.570579779-1274287'
pcs = PCS(access_token)


def _file(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename)
    f = open(filepath, 'rb')  # rb 模式
    return f


def test_info():
    """磁盘配额信息"""
    response = pcs.info()
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_upload():
    """上传"""
    response = pcs.upload('/apps/test_sdk/test.txt', _file('test1'),
                          ondup='overwrite', verify=False)
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_upload_tmpfile():
    """分片上传 - 上传临时文件"""
    response = pcs.upload_tmpfile(_file('test1'), verify=False)
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_upload_superfile():
    f1_md5 = pcs.upload_tmpfile(_file('test1'), verify=False).json()['md5']
    f2_md5 = pcs.upload_tmpfile(_file('test2'), verify=False).json()['md5']
    time.sleep(2)
    response = pcs.upload_superfile('/apps/test_sdk/super2.txt',
                                    [f1_md5, f2_md5], ondup='overwrite')
    logger.warn(response.status_code)
    assert response.ok
    assert response.json()
    logger.warn(response.json())


def test_download():
    response = pcs.download('/apps/test_sdk/super2.txt', verify=False)
    logger.warn(response.status_code)
    assert response.ok
    assert 'abc'.encode() in response.content


def test_download_range():
    test_upload_superfile()
    headers = {'Range': 'bytes=0-2'}
    response1 = pcs.download('/apps/test_sdk/super2.txt', headers=headers,
                             verify=False)
    assert response1.content == 'abc'.encode()
    headers = {'Range': 'bytes=3-5'}
    response2 = pcs.download('/apps/test_sdk/super2.txt', headers=headers,
                             verify=False)
    assert response2.content == 'def'.encode()


def test_mkdir():
    response = pcs.mkdir('/apps/test_sdk/testmkdir')
    logger.warn(response.status_code)
    assert response.json()
    if not response.ok:
        assert response.json()['error_code'] == 31061
    logger.warn(response.json())


def test_meta():
    response = pcs.meta('/apps/test_sdk/super2.txt')
    logger.warn(response.status_code)
    assert response.json()
    assert response.ok
    logger.warn(response.json())


def test_multi_meta():
    response = pcs.multi_meta(['/apps/test_sdk/super2.txt',
                              '/apps/test_sdk/testmkdir'])
    logger.warn(response.status_code)
    assert response.json()
    assert response.ok
    logger.warn(response.json())


def test_list_files():
    response = pcs.list_files('/apps/test_sdk/testmkdir')
    logger.warn(response.status_code)
    assert response.json()
    assert response.ok
    logger.warn(response.json())


def test_move():
    response = pcs.move('/apps/test_sdk/test.txt',
                        '/apps/test_sdk/testmkdir/a.txt')
    logger.warn(response.status_code)
    assert response.json()
    if not response.ok:
        assert response.json()['error_code'] == 31061
    logger.warn(response.json())


def test_multi_move():
    pcs.upload('/apps/test_sdk/test.txt', _file('test1'), verify=False)
    pcs.upload('/apps/test_sdk/b.txt', _file('test1'), verify=False)
    path_list = [
        ('/apps/test_sdk/test.txt', '/apps/test_sdk/testmkdir/b.txt'),
        ('/apps/test_sdk/b.txt', '/apps/test_sdk/testmkdir/a.txt'),
    ]
    time.sleep(2)
    response = pcs.multi_move(path_list)
    logger.warn(response.status_code)
    logger.warn(response.json())
    if not response.ok:
        assert response.json()['error_code'] == 31061


def test_copy():
    pcs.upload('/apps/test_sdk/test.txt', _file('test1'), verify=False)
    response = pcs.copy('/apps/test_sdk/test.txt',
                        '/apps/test_sdk/testmkdir/c.txt')
    logger.warn(response.status_code)
    logger.warn(response.json())
    if not response.ok:
        assert response.json()['error_code'] == 31061


def test_multi_copy():
    pcs.upload('/apps/test_sdk/test.txt', _file('test1'), verify=False)
    pcs.upload('/apps/test_sdk/b.txt', _file('test2'), verify=False)
    path_list = [
        ('/apps/test_sdk/test.txt', '/apps/test_sdk/testmkdir/b.txt'),
        ('/apps/test_sdk/b.txt', '/apps/test_sdk/testmkdir/a.txt'),
    ]
    time.sleep(2)
    response = pcs.multi_copy(path_list)
    logger.warn(response.status_code)
    logger.warn(response.json())
    if not response.ok:
        assert response.json()['error_code'] == 31061


def test_delete():
    pcs.upload('/apps/test_sdk/testmkdir/e.txt', _file('test3'), verify=False)
    time.sleep(2)
    response = pcs.delete('/apps/test_sdk/testmkdir/e.txt')
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_multi_delete():
    pcs.upload('/apps/test_sdk/testmkdir/e.txt', _file('test1'), verify=False)
    pcs.upload('/apps/test_sdk/testmkdir/d.txt', _file('test2'), verify=False)
    time.sleep(2)
    response = pcs.multi_delete(['/apps/test_sdk/testmkdir/e.txt',
                                '/apps/test_sdk/testmkdir/d.txt'])
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_search():
    response = pcs.upload('/apps/test_sdk/test.txt', _file('test1'),
                          ondup='overwrite', verify=False)
    response = pcs.search('/apps/test_sdk/', 'test')
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_thumbnail():
    response = pcs.thumbnail('/apps/test_sdk/testmkdir/404.png', 100, 100)
    logger.warn(response.status_code)
    logger.warn(repr(response.content[:10]))
    # im = Image.open(StringIO(response.content))
    # im.show()
    assert response.ok


def test_diff():
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', _file('test2'),
               ondup='overwrite', verify=False)
    response0 = pcs.diff()
    new_cursor = response0.json()['cursor']
    time.sleep(2)
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', str(time.time()),
               ondup='overwrite', verify=False)
    response1 = pcs.diff(cursor=new_cursor)
    new_cursor = response1.json()['cursor']
    time.sleep(2)
    pcs.upload('/apps/test_sdk/testmkdir/h.txt', str(time.time()),
               ondup='overwrite', verify=False)
    response2 = pcs.diff(cursor=new_cursor)
    logger.warn(response2.status_code)
    logger.warn(response2.json())
    assert response2.json()
    assert response2.ok


def test_video_convert():
    response = pcs.video_convert('/apps/test_sdk/testmkdir/test.mp4',
                                 'M3U8_320_240')
    logger.warn(response.status_code)
    logger.warn(response.content)
    assert response.ok


def test_list_streams():
    response1 = pcs.list_streams('image')
    logger.warn(response1.json())
    response2 = pcs.list_streams('doc', filter_path='/apps/test_sdk/test')
    logger.warn(response2.status_code)
    logger.warn(response2.json())
    assert response2.ok


def test_download_stream():
    response = pcs.download_stream('/apps/test_sdk/testmkdir/404.png',
                                   verify=False)
    logger.warn(response.status_code)
    logger.warn(repr(response.content[:10]))
    assert response.ok


def test_rapid_upload():
    content = ('a' * 1024 * 1024).encode('utf8')
    pcs.upload('/apps/test_sdk/testmkdir/upload.txt', content,
               ondup='overwrite', verify=False)
    time.sleep(3)
    response = pcs.rapid_upload('/apps/test_sdk/testmkdir/rapid.txt',
                                len(content), content_md5(content),
                                content_crc32(content),
                                slice_md5(content[:1024 * 256]),
                                ondup='overwrite')
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_add_download_task():
    url = 'http://img3.douban.com/pics/nav/logo_db.png'
    remote_path = '/apps/test_sdk/testmkdir/bdlogo.gif'
    response = pcs.add_download_task(url, remote_path)
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_query_download_tasks():
    url1 = 'http://img3.douban.com/pics/nav/lg_main_a11_1.png'
    url2 = 'http://img3.douban.com/pics/nav/logo_db.png'
    remote_path = '/apps/test_sdk/testmkdir/%s'
    task1 = pcs.add_download_task(url1, remote_path % os.path.basename(url1))
    task2 = pcs.add_download_task(url2, remote_path % os.path.basename(url2))
    time.sleep(2)
    task_ids = [task1.json()['task_id'], task2.json()['task_id']]
    response = pcs.query_download_tasks(task_ids)
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_list_download_tasks():
    response = pcs.list_download_tasks()
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_cancel_download_task():
    response = pcs.list_download_tasks()
    task_info = response.json()['task_info']
    logger.warn(response.json())
    if not task_info:
        assert True
    else:
        task_id = task_info[0]['task_id']
        response2 = pcs.cancel_download_task(task_id)
        logger.warn(response2.status_code)
        logger.warn(response2.json())
        assert response2.ok


def test_list_recycle_bin():
    pcs.upload('/apps/test_sdk/testmkdir/10.txt', _file('test2'),
               ondup='overwrite', verify=False)
    time.sleep(2)
    pcs.delete('/apps/test_sdk/testmkdir/10.txt')
    time.sleep(2)
    response = pcs.list_recycle_bin()
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_restore_recycle_bin():
    pcs.upload('/apps/test_sdk/testmkdir/10.txt', _file('test1'),
               ondup='overwrite', verify=False)
    pcs.delete('/apps/test_sdk/testmkdir/10.txt')
    time.sleep(2)
    response1 = pcs.list_recycle_bin()
    fs_id = response1.json()['list'][0]['fs_id']
    response = pcs.restore_recycle_bin(fs_id)
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_multi_restore_recycle_bin():
    pcs.upload('/apps/test_sdk/testmkdir/1.txt', _file('test2'),
               ondup='overwrite', verify=False)
    time.sleep(2)
    pcs.delete('/apps/test_sdk/testmkdir/1.txt')
    pcs.upload('/apps/test_sdk/testmkdir/2.txt', _file('test1'),
               ondup='overwrite', verify=False)
    time.sleep(2)
    pcs.delete('/apps/test_sdk/testmkdir/2.txt')
    time.sleep(2)
    response1 = pcs.list_recycle_bin()
    fs_ids = [x['fs_id'] for x in response1.json()['list'][:1]]
    response = pcs.multi_restore_recycle_bin(fs_ids)
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok


def test_clean_recycle_bin():
    response = pcs.clean_recycle_bin()
    logger.warn(response.status_code)
    logger.warn(response.json())
    assert response.ok
