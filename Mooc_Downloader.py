import os
import sys
import requests
import re
import time
import json

BIZ_ID = None

class Mooc_Spider:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    }
    dwrheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'content-Type': 'text/plain'
    }
    __session = requests.Session()
    apiurl = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getMocTermDto.dwr'
    resourceurl = 'https://www.icourse163.org/web/j/resourceRpcBean.getResourceToken.rpc'
    videourl = 'https://vod.study.163.com/eds/api/v1/vod/video'
    bizId = None
    tid = None
    streamurl = None
    title = None
    lessonId = None
    videoId = None
    signature = None
    videoname = None

    def run(self):
        self.__response = self.__session.get(self.url, headers=self.headers, timeout=5)
        self.csrfKey = self.__session.cookies['NTESSTUDYSI']
        Form_data = {
            'callCount': '1',
            'scriptSessionId': '${scriptSessionId}190',
            'httpSessionId': self.csrfKey,
            'c0-scriptName': 'CourseBean',
            'c0-methodName': 'getMocTermDto',
            'c0-id': '0',
            'c0-param0': 'number:' + str(self.tid),
            'c0-param1': 'number:0',
            'c0-param2': 'boolean:true',
            'batchId': str(int(time.time()*1000))
        }
        data = ''
        for key, value in Form_data.items():
            data += key + '=' + value + '\n'
        self.__response = self.__session.post(self.apiurl, data=data, timeout=5, headers=self.dwrheaders)
        tmp = self.__response.text
        if BIZ_ID:
            tmp = re.findall('.*id=%s.*' % str(BIZ_ID), tmp)[0]
            self.videoId = re.findall('contentId=(\d*)', tmp)[0]
            self.bizId = BIZ_ID
        else:
            tmp = re.findall('.*lessonId=%s.*' % self.lessonId, tmp)[0]
            self.videoId = re.findall('contentId=(\d*)', tmp)[0]
            self.bizId = re.findall('.id=(\d*)', tmp)[0]
        Form_data = {
            'csrfKey': self.csrfKey,
            'bizId': self.bizId,
            'bizType': 1,
            'contentType': 1
        }
        self.__response = self.__session.post(self.resourceurl, data=Form_data, timeout=5, headers=self.headers)
        tmp = json.loads(self.__response.text)
        self.signature = tmp['result']['videoSignDto']['signature']
        self.videoname = tmp['result']['videoSignDto']['name']
        Form_data = {
            'videoId': self.videoId,
            'signature': self.signature,
            'clientType': 1
        }
        self.__response = self.__session.post(self.videourl, data=Form_data, timeout=5, headers=self.headers)
        tmp = json.loads(self.__response.text)['result']['videos']
        now_quality = 1
        for each in tmp:
            if each['quality'] > now_quality:
                now_quality = each['quality']
                self.streamurl = each['videoUrl']
        pass

    def __init__(self, url):
        self.url = url
        self.tid = re.findall(u'tid=(\d*)', url)[0]
        self.lessonId = re.findall(u'&id=(\d*)', url)[0]


def download(url, filename):
    if filename.endswith('.mp4'):
        os.system('ffmpeg.exe -i %s ".\Download\%s"' % (url, filename))
    else:
        os.system('ffmpeg.exe -i %s ".\Download\%s.mp4"' % (url, filename))


# debugtext = 'https://www.icourse163.org/learn/SJZC-1449501164?tid=1449925443#/learn/content?type=detail&id=1214138367'

# spider = Mooc_Spider(sys.argv[1])
# spider = Mooc_Spider(debugtext)

if not os.path.exists('Download'):
    os.mkdir('Download')

url = input('输入网址：')
try:
    BIZ_ID = re.findall(u'cid=(\d*)', url)[0]
except:
    pass
spider = Mooc_Spider(url)

spider.run()
print(spider.streamurl, spider.videoname)
download(spider.streamurl, spider.videoname)

