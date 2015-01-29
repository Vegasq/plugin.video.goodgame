import sys
import re
import xbmcgui
import xbmcplugin
import requests
import httplib
import urllib
import urlparse


addon_handle = int(sys.argv[1])
base_url = sys.argv[0]
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'movies')


class GGKodi(object):
    avaliable_games = [
        {'tag': 'warcraft-iii-the-frozen-throne', 'title': 'Warcraft III'},
        {'tag': 'starcraft-ii-heart-of-the-swarm', 'title': 'Starcraft II'},
        {'tag': 'hearthstone-heroes-of-warcraft', 'title': 'Heartstone'},
        {'tag': 'heroes-of-the-storm', 'title': 'Heroes of the Storm'},
    ]
    idselector = '.*player\?(\w*)\\"'
    gg_api_url = "http://goodgame.ru/api/getchannelsbygame?game=%s&fmt=json"
    available_qualities = [240, 480, 720]

    def set_game(self, game):
        self.game = game

    def _build_url(self, query):
        return base_url + '?' + urllib.urlencode(query)

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
            url = self._build_url(game_info)
            li = xbmcgui.ListItem(game_info['title'],
                                  iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle,
                                        url=url,
                                        listitem=li,
                                        isFolder=True)
        xbmcplugin.endOfDirectory(addon_handle)

    def create_streams_menu(self):
        data = requests.get(self.gg_api_url % self.game)
        data = data.json()

        for id in data:
            stream_id = self._extract_id(data[id]['embed'])
            if not stream_id:
                continue

            for qualitie in self.available_qualities:
                url = 'http://hls.goodgame.ru/hls/%s_%s.m3u8' % (stream_id, qualitie)
                if not self._is_stream_avaliable(url):
                    continue
                li = xbmcgui.ListItem(
                    '[%sp] %s - %s' % (qualitie, data[id]['key'], data[id]['title']),
                    iconImage=data[id]['img'])
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

        xbmcplugin.endOfDirectory(addon_handle)


game = args.get('tag', None)
ggk = GGKodi()

if game is None:
    ggk.create_main_menu()
else:
    ggk.set_game(args['tag'][0])
    ggk.create_streams_menu()
