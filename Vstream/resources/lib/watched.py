# -*- coding: utf-8 -*-
# https://github.com/Kodi-vStream/venom-xbmc-addons
from more_itertools.more import replace
DEBUG = False


if DEBUG:

    import sys  # pydevd module need to be copied in Kodi\system\python\Lib\pysrc
    #sys.path.append('H:\Program Files\Kodi\system\Python\Lib\pysrc')

    try:
        import pydevd  # with the addon script.module.pydevd, only use `import pydevd`
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " + "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")

import xbmc

from resources.lib.db import cDb
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.gui.hoster import cHosterGui
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.comaddon import dialog, addon, isMatrix
from resources.lib.util import UnquotePlus

SITE_IDENTIFIER = 'cWatched'
SITE_NAME = 'Watched'


class cWatched:

    DIALOG = dialog()
    ADDON = addon()

    # Suppression d'un bookmark, d'une catégorie, ou tous les bookmarks
    def delWatched(self):
        oInputParameterHandler = cInputParameterHandler()
        sTitleWatched = oInputParameterHandler.getValue('sTitleWatched')
        sCat = oInputParameterHandler.getValue('sCat')

        if not sTitleWatched:  # confirmation if delete ALL
            if not self.DIALOG.VSyesno(self.ADDON.VSlang(30456)):
                return False

        meta = {}
        meta['titleWatched'] = sTitleWatched
        if sCat:
            meta['cat'] = sCat

        with cDb() as db:
            if db.del_watched(meta):
                self.DIALOG.VSinfo(addon().VSlang(30072))
                cGui().updateDirectory()
            return True

    # Suppression d'un bookmark depuis un Widget
    def delWatchedMenu(self):
        sTitle = xbmc.getInfoLabel('ListItem.OriginalTitle')
        if not sTitle:    # confirmation if delete ALL
            if not self.DIALOG.VSyesno(self.ADDON.VSlang(30456)):
                return False
        sCat = xbmc.getInfoLabel('ListItem.Property(sCat)')
        meta = {}
        meta['titleWatched'] = sTitle
        meta['cat'] = sCat
        with cDb() as db:
            if db.del_watched(meta):
                self.DIALOG.VSinfo(addon().VSlang(30072))
                cGui().updateDirectory()

            return True
        
    def setWatched(self):
        oInputParameterHandler = cInputParameterHandler()

        sCat = oInputParameterHandler.getValue('sCat') if oInputParameterHandler.exist('sCat') else xbmc.getInfoLabel('ListItem.Property(sCat)')
        iCat = 0
        if sCat:
            iCat = int(sCat)
        if iCat < 1 or iCat > 9:
            self.DIALOG.VSinfo('Error', self.ADDON.VSlang(30038))
            return

        meta = {}

        sSiteUrl = oInputParameterHandler.getValue('siteUrl') if oInputParameterHandler.exist('siteUrl') else xbmc.getInfoLabel('ListItem.Property(siteUrl)')
        sTitle = oInputParameterHandler.getValue('sMovieTitle') if oInputParameterHandler.exist('sMovieTitle') else xbmc.getInfoLabel('ListItem.Property(sCleanTitle)')
        sSite = oInputParameterHandler.getValue('sId') if oInputParameterHandler.exist('sId') else xbmc.getInfoLabel('ListItem.Property(sId)')
        sFav = oInputParameterHandler.getValue('sFav') if oInputParameterHandler.exist('sFav') else xbmc.getInfoLabel('ListItem.Property(sFav)')

        if sTitle == '':
            self.DIALOG.VSinfo('Error', 'Probleme sur le titre')
            return

        meta['siteurl'] = sSiteUrl
        meta['title'] = sTitle
        meta['site'] = sSite
        meta['fav'] = sFav
        meta['cat'] = sCat

        meta['icon'] = xbmc.getInfoLabel('ListItem.Art(thumb)')
        meta['fanart'] = xbmc.getInfoLabel('ListItem.Art(fanart)')
        try:
            # Comptages des marque-pages
            with cDb() as db:
                db.insert_watched(meta)
        except:
            pass
    
    def showMenu(self):
        oGui = cGui()
        addons = addon()

        oOutputParameterHandler = cOutputParameterHandler()
        oGui.addDir(SITE_IDENTIFIER, 'getWatched', addons.VSlang(30126), 'genres.png', oOutputParameterHandler)

        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('sCat', '1')       # films
        oGui.addDir(SITE_IDENTIFIER, 'getWatched', addons.VSlang(30120), 'films.png', oOutputParameterHandler)

        oOutputParameterHandler.addParameter('sCat', '2')       # saisons
        oGui.addDir(SITE_IDENTIFIER, 'getWatched', '%s/%s' % (self.ADDON.VSlang(30121), self.ADDON.VSlang(30122)), 'series.png', oOutputParameterHandler)

        oOutputParameterHandler.addParameter('sCat', '5')       # Divers
        oGui.addDir(SITE_IDENTIFIER, 'getWatched', self.ADDON.VSlang(30410), 'buzz.png', oOutputParameterHandler)

        oGui.setEndOfDirectory()

    def getWatched(self):
        oGui = cGui()

        oInputParameterHandler = cInputParameterHandler()
        meta = {}
        catFilter = oInputParameterHandler.getValue('sCat')
        sSite = oInputParameterHandler.getValue('sId') if oInputParameterHandler.exist('sId') else xbmc.getInfoLabel('ListItem.Property(sId)')
        title = oInputParameterHandler.getValue('sMovieTitle') if oInputParameterHandler.exist('sMovieTitle') else xbmc.getInfoLabel('ListItem.Property(sCleanTitle)')
        #meta['cat'] = catFilter
        #meta['site'] = sSite
        meta['title'] = title
       
        

        with cDb() as DB:
            row = DB.get_allwatched(meta)
            if not row:
                oGui.setEndOfDirectory()
                return

            for data in row:

                try:
                    title = data['title'].encode('utf-8')
                except:
                    title = data['title']

                try:
                    try:
                        siteurl = data['siteurl'].encode('utf-8')
                    except:
                        siteurl = data['siteurl']

                    if isMatrix():
                        siteurl = UnquotePlus(siteurl.decode('utf-8'))
                        title = str(title, 'utf-8')
                    else:
                        siteurl = UnquotePlus(siteurl)

                    sTitleWatched = data['title_id']
                    site = data['site']
                    function = data['fav']
                    cat = data['cat']
                    #if cat == '2':
                        #cat= '4'
                        #catEp = '2'
                    sSeason = data['season']
                    sTmdbId = data['tmdb_id'] if data['tmdb_id'] != '0' else None
                    

                    if catFilter is not False and cat != catFilter:
                        continue

                    oOutputParameterHandler = cOutputParameterHandler()
                    oOutputParameterHandler.addParameter('siteUrl', siteurl)
                    oOutputParameterHandler.addParameter('sMovieTitle', title)
                    oOutputParameterHandler.addParameter('sTmdbId', sTmdbId)
                    oOutputParameterHandler.addParameter('sTitleWatched', sTitleWatched)
                    oOutputParameterHandler.addParameter('sSeason', sSeason)
                    oOutputParameterHandler.addParameter('sCat', cat)
                    oOutputParameterHandler.addParameter('isWatched', True)

                    meta = {}
                    meta['title'] = sTitleWatched
                    resumetime, totaltime = DB.get_resume(meta)
                    oOutputParameterHandler.addParameter('ResumeTime', resumetime)
                    oOutputParameterHandler.addParameter('TotalTime', totaltime)


                    if cat == '1':
                        oListItem = oGui.addMovie(site, function, title, 'films.png', '', title, oOutputParameterHandler)
                    elif cat == '2':
                        oListItem = oGui.addSeason(site, function, title, 'series.png', '', title, oOutputParameterHandler)
                    elif cat == '5':
                        oListItem = oGui.addMisc(site, function, title, 'buzz.png', '', title, oOutputParameterHandler)
                    #elif catEp == '2' :
                        #oListItem = oGui.addTV(site, function, title, 'series.png', '', title, oOutputParameterHandler)
                    
                    else:
                        oListItem = oGui.addTV(site, function, title, 'series.png', '', title, oOutputParameterHandler)

                    oOutputParameterHandler.addParameter('sTitleWatched', sTitleWatched)
                    oOutputParameterHandler.addParameter('sCat', cat)
                    oListItem.addMenu(SITE_IDENTIFIER, 'delWatched', self.ADDON.VSlang(30412), oOutputParameterHandler)

                except Exception as e:
                    pass

        # Vider toute la catégorie n'est pas accessible lors de l'utilisation en Widget
        if not xbmc.getCondVisibility('Window.IsActive(home)'):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('sCat', catFilter)
            oGui.addDir(SITE_IDENTIFIER, 'delWatched', self.ADDON.VSlang(30211), 'trash.png', oOutputParameterHandler)

        oGui.setEndOfDirectory()

        return
