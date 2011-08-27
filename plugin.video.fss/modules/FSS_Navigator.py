import os
import sys

import urllib
import urllib2
import cookielib
import md5

import time
import datetime

from time import strftime
from time import strptime
from datetime import timedelta
from datetime import date

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import FSS_Scraper

fss_addon = xbmcaddon.Addon("plugin.video.fss");
__scraper__ = FSS_Scraper.FSS_Scraper()


class FSS_Navigator:

    def __init__(self):
        self.artwork   = os.path.join(fss_addon.getAddonInfo('path'),'image')
        self.offline   = os.path.join(fss_addon.getAddonInfo('path'),'image\offline')
        self.username  = fss_addon.getSetting("username")
        self.password  = fss_addon.getSetting("password")
        self.passhash  = md5.new(self.password).hexdigest()
        self.loginData = urllib.urlencode(
            {'do' : 'login',
             'url' : __scraper__.memberurl,
             'vb_login_md5password' : self.passhash,
             'vb_login_md5password_utf' : self.passhash,
             'vb_login_username' : self.username,
             'vb_login_password' : 0})
        
        # Channel Name Array
        self.channelname = ['Sky Sports 1',
                            'Sky Sports 2',
                            'Sky Sports 3',
                            'Sky Sports 4',
                            'Sky Sports News',
                            'ESPN UK',
                            'ESPN US',
                            'ESPN 2',
                            'Setanta Sports Canada',
                            'Setanta Sports Australia',
                            'ESPNU College Sports',
                            'Sky News HD', # Channel is Silverlight - not supported
                            'WBC Boxing', # Weird channel - not supported
                            'Fox Soccer Channel',
                            'Fox Soccer Plus']

    def login(self, openurl):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.open(__scraper__.loginurl, self.loginData)
        link = opener.open(openurl).read()
        return link

    def settings(self):
        if self.username != '' and self.password != '':
            link = self.login(__scraper__.memberurl)
            if (__scraper__.account_check(link) == False):
                self.check_settings('-- Your username and/or password is incorrect. --')
            else:
                self.menu()
        else:
            self.check_settings('-- Settings not defined or there is a problem.  Please check your settings. --')

    def check_settings(self, error_string):
	u=sys.argv[0]+"?url=Settings&mode=3"
	listfolder = xbmcgui.ListItem(error_string)
	listfolder.setInfo('video', {'Title': 'Settings not defined or there is a problem.  Please check your settings.'})
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def menu(self):
	u=sys.argv[0]+"?url=Channels&mode=1"
	listfolder = xbmcgui.ListItem('Channels')
	listfolder.setInfo('video', {'Title': 'Channels'})
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

	u=sys.argv[0]+"?url=Schedule&mode=2"
	listfolder = xbmcgui.ListItem('Schedule')
	listfolder.setInfo('video', {'Title': 'Schedule'})
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)
  
	u=sys.argv[0]+"?url=Settings&mode=3"
	listfolder = xbmcgui.ListItem('Settings')
	listfolder.setInfo('video', {'Title': 'Settings'})
	xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, listfolder, isFolder=1)

	xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def list_channels(self):
        for i in range (1,16):
            if i != 12:
                if i != 13:
                    slist = self.channelname[i-1]
                    isPlayable = 'true'
                    chanId = str(i)
                    isFolder=False
                    playUrl = urllib.quote_plus(__scraper__.channelurl %chanId)
                    mode = '5'
                    self.add_nav_item(slist, isPlayable, chanId, isFolder, playUrl, mode)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def add_nav_item(self, slist, isPlayable, chanId, isfolder, playUrl, mode):
        label = ''.join(slist)
        listitem = xbmcgui.ListItem(label=label)
        listitem.setInfo('video' , {'title': label})
        listitem.setProperty('IsPlayable', isPlayable)
#        listitem.setIconImage(os.path.join(self.artwork, 'ch%s.png' %chanId))
        u=sys.argv[0]+"?url="+ playUrl + "&mode=%s" %mode + "&name="+urllib.quote_plus(label)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=listitem, isFolder=isfolder)

    def play_stream(self, url):
        link = self.login(url)
        rtmpUrl = __scraper__.build_rtmp_url(link, url)
        item = xbmcgui.ListItem(path=rtmpUrl)
        return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

    def list_schedule(self):
        today = date.today()
        for i in range (0, 7):
            td = timedelta(days=i)
            d1 = (today + td).timetuple()
            Day = strftime("%A", d1)
            Date = __scraper__.date_to_ordinal(d1.tm_mday)
            usedate = __scraper__.convert_2_fssurldate(today + td)
            Month = strftime("%B", d1)
            self.add_nav_item([Day,' ',Date,' ',Month],
                              'false',
                              '0',
                              True,
                              usedate,
                              '6')
       	xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def list_daily_schedule(self, date):
        day = datetime.datetime(*(time.strptime(date, "%Y-%m-%d"))[0:6])
        today = str(day)
        link = self.login(__scraper__.dailyscheduleurl %today)
        __scraper__.get_schedule_item(link, today)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
