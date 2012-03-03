# -*- coding: utf-8 -*-
# Copyright 2010 xbmcdude
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import xbmc, xbmcgui, xbmcplugin, urllib, urllib2, re
import os, xbmcaddon, sys
import time

Addon = xbmcaddon.Addon('plugin.video.own3d.tv')

class own3Dvideo :
        def __init__( self, Addon, prefetch=False ):
                self.Title = None
                self.Channel = None
                self.Duration = None
                self.Thumbnail = None
                

        
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def addLink(name,url,iconimage,user,duration):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={
                "Title": name, "Plot": name,"TVShowTitle": user, "Description": "ads",
                "Duration" : duration, "VideoResolution": "720", "Director": user} )
        cm = []
        title = (Addon.getLocalizedString( 2005 ) % (user) )
        browse =  'XBMC.Container.Refresh(%s?mode=listvids&submode=channel&name=%s&channelid=-1)' % ( sys.argv[0],user )
        cm.append((title, browse  ))

        subscrib=Addon.getSetting('favorite_channels').split(',')
        if (subscrib.count(user)==0):
                title = (Addon.getLocalizedString( 2006 ) % (user) )                
                browse =  'XBMC.Container.Refresh(%s%s&subscribeuser=%s)' % ( sys.argv[0],sys.argv[2],user )
        else:
                title = (Addon.getLocalizedString( 2007 ) % (user) )                
                browse =  'XBMC.Container.Refresh(%s%s&unsubscribeuser=%s)' % ( sys.argv[0],sys.argv[2],user )
        
        cm.append((title, browse  ))

        if len(cm) > 0:
            liz.addContextMenuItems( cm, replaceItems=False )
            
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,channelid,mode,submode,iconimage):
        u=sys.argv[0]+"?mode="+urllib.quote_plus(mode)+"&submode="+urllib.quote_plus(submode)+"&channelid="+urllib.quote_plus(str(channelid))+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def GrabHTMLFromSite (url, postdata):
        req = urllib2.Request(url,postdata)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14')
        response = urllib2.urlopen(req)
        lines=response.read()
        response.close()
    
        return lines

def GrabValueReg (lines, regexpr):
        a=re.compile(regexpr,re.S)
        match=a.findall(lines)
        if len(match)>0:
                return match[0]
        else:
                return ""
        
def GrabValueRegExprFromSite (url, regexpr):
        lines=GrabHTMLFromSite(url,"")
        return GrabValueReg(lines,regexpr)

def FormatVideoName(user,title):
        value=Addon.getSetting('show_channelname_inlist')
        if value == "true":
                return ('[%s] %s' % (user,title))
        else:
                return title

def SubscribeStrToList(subscrstr):
        retlist = []
        
        retlist=subscrstr.split(',')
        return retlist
        
def SubscribeListToStr(subscribers):
        retstr = ""
        if subscribers.count("")>0:
                subscribers.remove("")        
        if len(subscribers)>1:
                retstr =  ",".join(subscribers)
        elif len(subscribers)==1:
                retstr= subscribers[0]
        else:
                retstr = ""
 
        return retstr
        
def SubscribeUser(user):
        subscrib=SubscribeStrToList(Addon.getSetting('favorite_channels'))
        if (subscrib.count(user)==0):
                subscrib.append(user)

        list_subsc=SubscribeListToStr(subscrib)

        Addon.setSetting('favorite_channels',list_subsc)
        return

def UnSubscribeUser(user):
        subscrib=SubscribeStrToList(Addon.getSetting('favorite_channels'))
        if (subscrib.count(user)>0):
                subscrib.remove(user)
        list_subsc=SubscribeListToStr(subscrib)

        Addon.setSetting('favorite_channels',list_subsc)
        return

def GrabVideoList(submode,gameid,channelname):
        maxlines = 25;
        pagenumber = 1;
        base = "http://www.own3d.tv/videos/";
        url = base + "?search=&sort="+submode+"&time=week";
        if int(gameid)>0:
                url=url+"&search_game="+str(gameid)
        regexpr = '/watch/(\d+?)\".+?title="(.+?)" class.+?/game/.+?">(.+?)\<.+?(\d[\s\w]+?ago).+?\"/(.+?)\".+?(\d+?:\d+?)&nbsp;'                
        lines=GrabHTMLFromSite(url,"")         
        xbmc.log(url);
        a=re.compile(regexpr,re.S)
        match=a.findall(lines)
        for videoid,title,game,date,user,duration in match:
            url=sys.argv[0]+"?mode="+urllib.quote_plus("videos")+"&channelid="+urllib.quote_plus(str(videoid))+"&name="+urllib.quote_plus(title)
            addLink(FormatVideoName(user,title),url,'http://img.own3d.tv/thumbnails/tn_'+videoid+'__1.jpg',user,duration)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
            
        return 1

def GrabChannel(submode,channelid,channelname):
        maxlines = 25;
        pagenumber = 1

        base = "http://www.own3d.tv/"+channelname;
        # no channelid, so grab it
        if int(channelid)<0:
                channelid=GrabValueRegExprFromSite(base,"xajax_get_user_videos \((\d+),")
       
        url = base+ '?s=user&user_name='+channelname
        data = "xjxfun=get_user_videos&xjxr=1287432135245&xjxargs[]=N"+str(channelid)+"&xjxargs[]=Sall&xjxargs[]=N"+str(maxlines)+"&xjxargs[]=S&xjxargs[]=Strue&xjxargs[]=N"+str(pagenumber)
        regexpr = 'src="http://img.own3d.tv/thumbnails/tn_(.+?)__1.jpg" alt="(.+?)".+?\t(\d+:\d+)&nbsp.+?\/game/(.+?)".+?(\d+ \w+ ago).+?href="/(.+?)">' 
        lines=GrabHTMLFromSite(url,data)
        a=re.compile(regexpr,re.S)
        match=a.findall(lines)
        for videoid,title,duration,game,date,user in match:
            url=sys.argv[0]+"?mode="+urllib.quote_plus("videos")+"&channelid="+urllib.quote_plus(str(videoid))+"&name="+urllib.quote_plus(title)
            addLink(FormatVideoName(user,title) ,url,'http://img.own3d.tv/thumbnails/tn_'+videoid+'__1.jpg',user,duration)

#        xbmcplugin.setPluginCategory( handle=self._handle, category=channelname )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
            
        return 1


        
def ShowVideo(videoid,channelname):
    base = "http://www.own3d.tv/video/"+str(videoid);

    lines=GrabHTMLFromSite(base,"")

    a=re.compile('escape\(\'\?(.+?)&')
    tempid=a.findall(lines)[0]

    url="http://vodcdn.ec.own3d.tv/";

    hqurl=GrabValueReg(lines,'HQUrl: \'(videos/.*?\\.mp4)\'')
    add=hqurl
    
    value=Addon.getSetting('play_hd')
    if value == "true":
            hdurl=GrabValueReg(lines,'HDUrl: \'(videos/.*?\\.mp4)\'')
            if hdurl!="":
                 add=hdurl
    
    if add is None:
        xbmc.log('No video found!')
    else:
        url=url+add+'?'+tempid;

    xbmc.log("playing: "+url)
    thumbnailImage='http://img.own3d.tv/thumbnails/tn_'+videoid+'__1.jpg'
    item = xbmcgui.ListItem(GrabValueReg(lines,'\t\<span style=\"float:left;\"\>([^"]+?)\</span\>\<img src=\"templates/own3d'),thumbnailImage,thumbnailImage)
    plot=GrabValueReg(lines,'<span id="right_desc_long" style="display:.+?">\s+([\w\d].+?)&nbsp;<a href')
    plot=re.sub(r'<[^>]*?>', "", plot).strip()
    item.setProperty("Plot",plot)
    item.setProperty("VideoResolution",GrabValueReg(lines,'<meta name="video_width" content="(\d+)" />'))
    item.setInfo( type="Video", infoLabels={
                "Title": name, "Plot": plot , "TVShowTitle": channelname, "Description": plot
                } )
    xbmc.Player().play(url,item)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

    return 1

def ShowLiveVideo(videoid,title):
    xbmc.log("rtmp play")   
    item = xbmcgui.ListItem("RTMPLocal")
    plot="live"
    baseinfo="http://www.own3d.tv/livecfg/"+str(videoid)
    lines=GrabHTMLFromSite(baseinfo,"")
    channelname=GrabValueReg(lines,'owner="(.+?)"')
    xbmc.log(channelname)
    match = re.compile('quality="0" name="(.+?)"').findall(lines)
    print 'match = '+str(len(match))
    l=0
    p_path = None
    for i in match:
        if len(i) > l:
            l = len(i)
            p_path = i
            print 'p_path = '+p_path
        else: continue
   
    pageurl = ' pageUrl='+GrabValueReg(lines,'ownerLink="(.+?)"')
    playpath = ' Playpath='+p_path
    try:
        tcUrl = 'rtmp://fml.2010.edgecastcdn.net:1935/202010?'+playpath.split('?')[1][:28]
    except:
        tcUrl = 'rtmp://fml.2010.edgecastcdn.net:1935/202010?'+playpath.split('=')[1]
    swf = ' swfUrl=http://static.ec.own3d.tv/player/Own3dPlayerV2_86.swf swfVfy=True Live=True'
    url = tcUrl+pageurl+playpath+swf
    item.setInfo( type="Video", infoLabels={"Title": title, "Plot": plot , "TVShowTitle": channelname, "Description": plot} )
    xbmc.log(str(channelname).lower()+"_"+str(videoid))
    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, item)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return 1

def MySubscriptions():
    channels=Addon.getSetting('favorite_channels')
    for channel in channels.split(','):
            if len(channel)>0:
                    addDir(channel,-1,'listvids','channel','');
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

    return 1

def ListLive(gameid):
        #videoid=13574
        #user="clgame"
        duration=""
        #addLink("[LIVE] "+str(title) ,url,'http://img.hw.own3d.tv/live/big_live_tn_'+str(videoid)+'_.jpg?'+str(time.time()),user,duration)
        
        base = "http://www.own3d.tv/livestreams/";
        url = base + "?search=&time=week&type=live";
        xbmc.log(url)
        if int(gameid)>0:
                url=url+"&search_game="+str(gameid)
        regexpr = 'a href="/live/(\d+?)\".+?title="(.+?)"'
        lines=GrabHTMLFromSite(url,"")
        a=re.compile(regexpr,re.S)
        match=a.findall(lines)
        #xbmc.log(str(match))
        for videoid,title in match:
            url=sys.argv[0]+"?mode="+urllib.quote_plus("livevideos")+"&channelid="+urllib.quote_plus(str(videoid))+"&name="+urllib.quote_plus(title)
            addLink("[LIVE] "+str(title) ,url,'http://img.hw.own3d.tv/live/big_live_tn_'+str(videoid)+'_.jpg?'+str(time.time()),title,duration)
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        

def ListGames():
        addDir('League of Legends',163,'gamec','','');
        addDir('Battlefield 2',10,'gamec','','');
        addDir('Battlefield Bad Company 2',78,'gamec','','');
        addDir('Bloodline Champions',300,'gamec','','');
        addDir('Counter-Strike',4,'gamec','','');
        addDir('Counter-Strike: Source',5,'gamec','','');
        addDir('Darkfall ',399,'gamec','','');
        addDir('StarCraft II',42,'gamec','','');
        addDir('Warcraft III',19,'gamec','','');
        addDir('World of Warcraft ',20,'gamec','','');
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return 1

def GameCategories(parentgameid):
    addDir(Addon.getLocalizedString( 2010 ),parentgameid,'listvids','views','');
    #addDir(Addon.getLocalizedString( 2011 ),parentgameid,'listvids','being-watched','');
    addDir(Addon.getLocalizedString( 2012 ),parentgameid,'listvids','date','');
    addDir(Addon.getLocalizedString( 2014 ),parentgameid,'listlive','','');
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

    return 1
   
def Categories():
    addDir(Addon.getLocalizedString( 2010 ),0,'listvids','views','');
    #addDir(Addon.getLocalizedString( 2011 ),0,'listvids','being-watched','');#dosent seem to work?
    addDir(Addon.getLocalizedString( 2012 ),0,'listvids','date','');
    addDir(Addon.getLocalizedString( 2013 ),0,'listgames','','');
    addDir(Addon.getLocalizedString( 2014 ),0,'listlive','','');
    addDir(Addon.getLocalizedString( 2015 ),0,'mysubscriptions','','');
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

    return 1

params=get_params()
channelid=None
name=None
mode=None
submode=None
subscribeuser=None
unsubscribeuser=None

try:
        channelid=urllib.unquote_plus(params["channelid"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=urllib.unquote_plus(params["mode"])
except:
        pass
try:
        submode=urllib.unquote_plus(params["submode"])
except:
        pass
try:
        subscribeuser=urllib.unquote_plus(params["subscribeuser"])
except:
        pass
try:
        unsubscribeuser=urllib.unquote_plus(params["unsubscribeuser"])
except:
        pass

if subscribeuser!=None:
        SubscribeUser(subscribeuser)
if unsubscribeuser!=None:
        UnSubscribeUser(unsubscribeuser)        

if mode==None:
    Categories()       
elif mode=="listgames":
    ListGames()
elif mode=="gamec":
    GameCategories(channelid)            
elif mode=="mysubscriptions":
     MySubscriptions()           
elif mode=="listlive":
     ListLive(channelid)   
elif mode=="listvids":
     if submode == "channel":
         GrabChannel(submode,channelid,name)
     else:
         GrabVideoList(submode,channelid,name)
elif mode=="videos":
     ShowVideo(channelid,name)       
elif mode=="livevideos":
     ShowLiveVideo(channelid,name)       

