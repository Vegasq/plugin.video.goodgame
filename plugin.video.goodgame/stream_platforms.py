#!/usr/bin/env python
# Copyright (c) 2015 Niko Yakovlev <vegasq@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
import requests
import re
import httplib
from urlparse import urlparse


class StreamPlatform(object):
    def is_directory_based(self):
        return self._is_directory_based

    def _is_stream_avaliable(self, url):
        host_name = urlparse(url).netloc
        c = httplib.HTTPConnection(host_name)
        c.request("HEAD", url)
        if c.getresponse().status == 200:
            return True
        return False

    def get_streams(self):
        pass

    def get_menu(self):
        pass


class CyberGame(StreamPlatform):
    _is_directory_based = False

    get_channels = "http://api.cybergame.tv/w/streams2.php"
    get_channels_data = "http://api.cybergame.tv/w/streams2.php?"
    channel_src = "http://stream1.cybergame.tv:8080/premium2/%s.m3u8"

    def _get_channels(self):
        channels = requests.get(self.get_channels).json()
        request_tail = "&channels[]=" + "&channels[]=".join(channels)
        info = requests.get("%s%s" % (self.get_channels_data,
                                      request_tail)).json()
        result = []
        for channel in info:
            url = self.channel_src % channel['channel name']
            if channel['online'] != "1" or not self._is_stream_avaliable(url):
                continue

            result.append({
                'title': channel['channel name'],
                'url': url,
                'is_folder': False,
                'image': channel['thumbnail'],
            })
        return result

    def get_streams(self, game=''):
        return self._get_channels()

    def get_menu(self):
        return []


class GoodGame(StreamPlatform):
    _is_directory_based = True
    idselector = '.*player\?(\w*)\\"'
    gg_api_url = "http://goodgame.ru/api/getchannelsbygame?game=%s&fmt=json"
    stream_direct_url = 'http://hls.goodgame.ru/hls/%s_%s.m3u8'
    available_qualities = [240, 480, 720]
    DEBUG = False

    # TODO: Well... I beleave we need some way to get this data from site.
    avaliable_games = [
        {
            'title': 'Warcraft III',
            'tag': 'warcraft-iii-the-frozen-throne',
            'cover': 'war3.png'
        },
        {
            'title': 'Starcraft II',
            'tag': 'starcraft-ii-heart-of-the-swarm',
            'cover': 'sc2.png'
        },
        {
            'title': 'Heartstone',
            'tag': 'hearthstone-heroes-of-warcraft',
            'cover': 'http://goodgame.ru/files/logotypes/gm_38_mc4E_poster.jpg'
        },
        {
            'title': 'Heroes of the Storm',
            'tag': 'heroes-of-the-storm',
            'cover': 'hots.png'
        },
        {
            'title': 'DotA 2',
            'tag': 'dota-2',
            'cover': 'http://goodgame.ru/files/logotypes/gm_19_PruP_poster.jpg'
        },
        {
            'title': 'League of Legends',
            'tag': 'league-of-legends',
            'cover': 'http://goodgame.ru/files/logotypes/gm_21_UuSM_poster.jpg'
        },
        {
            'title': 'Counter Strike: GO',
            'tag': 'counter-strike-global-offensive',
            'cover': 'http://goodgame.ru/files/logotypes/gm_25_OwBH_poster.jpg'
        },
    ]

    def _extract_id(self, src):
        data = re.search(self.idselector, src)
        if not data:
            return False
        return data.group(1)

    def get_streams(self, game=False):
        if not game:
            return []

        data = requests.get(self.gg_api_url % game)
        data = data.json()

        avaliable_streams = []
        for id in data:
            stream_id = self._extract_id(data[id]['embed'])
            if not stream_id:
                if self.DEBUG:
                    print('ID not found: %s' % data[id]['key'])
                    print('            : %s' % data[id]['title'])
                    print('\n')
                continue

            for qualitie in self.available_qualities:
                url = self.stream_direct_url % (stream_id, qualitie)
                if not self._is_stream_avaliable(url):
                    if self.DEBUG:
                        print('M3U not found: %s' % data[id]['key'])
                        print('             : %s' % data[id]['title'])
                        print('             : %s' % url)
                        print('             : %s' % data[id]['embed'])
                        print('\n')
                    continue

                avaliable_streams.append({
                    'title': '[%sp] %s - %s' % (
                        qualitie, data[id]['key'], data[id]['title']),
                    'url': url,
                    'is_folder': False,
                    'image': data[id]['img']
                })
        return avaliable_streams

    def get_menu(self):
        return self.avaliable_games
