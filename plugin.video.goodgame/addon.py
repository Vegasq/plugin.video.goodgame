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

import sys
import re
import requests
import httplib
import urllib

from wrappers import get_kodi
from wrappers import get_game_tag


class GGKodi(object):
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
    idselector = '.*player\?(\w*)\\"'
    gg_api_url = "http://goodgame.ru/api/getchannelsbygame?game=%s&fmt=json"
    stream_direct_url = 'http://hls.goodgame.ru/hls/%s_%s.m3u8'
    available_qualities = [240, 480, 720]

    def __init__(self, kodi):
        self._kodi = kodi

    def set_game(self, game):
        self.game = game

    def _build_url(self, query):
        return sys.argv[0] + '?' + urllib.urlencode(query)

    def _extract_id(self, src):
        data = re.search(self.idselector, src)
        if not data:
            return False
        return data.group(1)

    def _is_stream_avaliable(self, url):
        c = httplib.HTTPConnection('hls.goodgame.ru')
        c.request("HEAD", url)
        if c.getresponse().status == 200:
            return True
        return False

    def create_main_menu(self):
        for game_info in self.avaliable_games:
            self._kodi.add(
                title=game_info['title'],
                url=self._build_url(game_info),
                image=self._kodi.image(game_info['cover'])
            )
        self._kodi.commit()

    def create_streams_menu(self):
        data = requests.get(self.gg_api_url % self.game)
        data = data.json()

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

                self._kodi.add(
                    title='[%sp] %s - %s' % (
                        qualitie, data[id]['key'], data[id]['title']),
                    url=url,
                    is_folder=False,
                    image=data[id]['img']
                )

        self._kodi.commit()


if __name__ == '__main__':
    kodi_wrapper = get_kodi()
    game_tag = get_game_tag(kodi_wrapper)
    ggk = GGKodi(kodi_wrapper)

    if game_tag is False:
        ggk.create_main_menu()
    else:
        ggk.set_game(game_tag)
        ggk.create_streams_menu()
