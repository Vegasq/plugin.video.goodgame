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
import urlparse
try:
    import xbmcgui
    import xbmcplugin
    addon_handle = int(sys.argv[1])
    xbmcplugin.setContent(addon_handle, 'movies')
    is_xbmc = True
except ImportError:
    is_xbmc = False


class GenericWrapper(object):
    _is_kodi = False
    def is_kodi(self):
        return self._is_kodi


class FakeWrapper(GenericWrapper):
    _is_kodi = False
    def add(self, *args, **kwargs):
        print('Item added: %s' % kwargs['title'])
        print('\n')

    def commit(self, *args, **kwargs):
        pass


class KodiWrapper(GenericWrapper):
    _is_kodi = True
    def add(self, title, url, is_folder=True, image='DefaultFolder.png'):
        li = xbmcgui.ListItem(title, iconImage=image)
        self._add_to_dir(li, url, is_folder)

    def _add_to_dir(self, li, url, is_folder):
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=is_folder)

    def commit(self):
        xbmcplugin.endOfDirectory(addon_handle)


def get_kodi():
    if is_xbmc:
        return KodiWrapper()
    else:
        return FakeWrapper()

def get_game_tag(kodi):
    if kodi.is_kodi() is False:
        return 'starcraft-ii-heart-of-the-swarm'

    args = urlparse.parse_qs(sys.argv[2][1:])
    if 'tag' in args:
        return args['tag'][0]

    return False
