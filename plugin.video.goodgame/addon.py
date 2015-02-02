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

import inspect
import sys
import urllib

from wrappers import get_kodi
from wrappers import get_args

import stream_platforms


class Screen():
    _platform = None

    def __init__(self):
        self._args = get_args()
        self._kodi = get_kodi()
        self._parse_args()

    def _build_url(self, query):
        query.pop('title')
        return sys.argv[0] + '?' + urllib.urlencode(query)

    def _parse_args(self):
        if 'platform' not in self._args:
            # MainMenu
            self._platform = stream_platforms.PlatformsMenu()
        else:
            # Search for platform in platforms
            for platform in stream_platforms.__dict__:
                kls = stream_platforms.__dict__[platform]
                if (
                    inspect.isclass(kls) and
                    issubclass(kls, stream_platforms.StreamPlatform) and
                    kls != stream_platforms.StreamPlatform and
                    self._args['platform'][0] == platform
                ):
                    self._platform = stream_platforms.__dict__[platform]()

    def display(self):
        menu = self._platform.display(self._args)
        for item in menu:
            self._kodi.add(
                title=item['title'],
                url=self._build_url(item),
                image=self._kodi.image(item['cover']),
                is_folder=item['is_folder']
            )
        self._kodi.commit()


if __name__ == '__main__':
    screen = Screen()
    screen.display()
