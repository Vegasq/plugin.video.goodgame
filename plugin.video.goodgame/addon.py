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
import sys
import re
import requests
import httplib
import urllib

from wrappers import get_kodi
from wrappers import get_game_tag

import stream_platforms


class StreamViewer(object):
    DEBUG = False

    def __init__(self, kodi, stream_platform):
        self._kodi = kodi
        self._platform = stream_platform

    def set_game(self, game):
        self.game = game

    def _build_url(self, query):
        return sys.argv[0] + '?' + urllib.urlencode(query)

    def create_main_menu(self):
        for game_info in self._platform.get_menu():
            self._kodi.add(
                title=game_info['title'],
                url=self._build_url(game_info),
                image=self._kodi.image(game_info['cover'])
            )
        self._kodi.commit()

    def create_streams_menu(self):
        streams = self._platform.get_streams(game=self.game)
        for stream in streams:
            self._kodi.add(**stream)
        self._kodi.commit()


if __name__ == '__main__':
    kodi_wrapper = get_kodi()
    stream_platform = stream_platforms.GoodGame()
    game_tag = get_game_tag(kodi_wrapper)
    sv = StreamViewer(kodi_wrapper, stream_platform)

    if game_tag is False and stream_platform.is_directory_based():
        sv.create_main_menu()
    else:
        sv.set_game(game_tag)
        sv.create_streams_menu()
