# -*- coding: utf-8 -*-

PREFIX = '/video/schweizerfernsehen'
NAME = L('Title')
ART = 'art.png'
ICON = 'icon.png'

API_BASE = 'http://www.srf.ch/podcasts'
API_DIR = 'http://www.srf.ch/play/tv/episodesfromshow?layout=json&id='
API_ITEM = 'https://il.srgssr.ch/integrationlayer/1.0/ue/srf/video/play/%s.json'

###############################################################################
def Start():

    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)

    HTTP.CacheTime = CACHE_1HOUR

    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)


####################################################################################################
# Main Menu is static
@handler(PREFIX, NAME, art=ART, thumb=ICON)
def VideoMainMenu():

    oc = ObjectContainer(title1=L('Title'))

    oc.add(DirectoryObject(key=Callback(SubMenu, title=L('Alle TV-Sendungen'), url='pt-tv'), title=L('Alle TV-Sendungen')))
    oc.add(DirectoryObject(key=Callback(SubMenu, title='SRF 1', url='pr-srf-1'), title='SRF 1'))
    oc.add(DirectoryObject(key=Callback(SubMenu, title='SRF zwei', url='pr-srf-2'), title='SRF zwei'))
    oc.add(DirectoryObject(key=Callback(SubMenu, title='SRF info', url='pr-srf-info'), title='SRF info'))

    return oc


####################################################################################################
# List shows of the selected channel
@route(PREFIX + '/submenu')
def SubMenu(title, url):

    oc = ObjectContainer(title1=L('Title'), title2=title)

    # Search data for the choosen channel
    try:
        source = HTML.ElementFromURL(API_BASE)
    except Exception as e:
        Log.Error(e)
        return ObjectContainer(header=L('Empty'), message=L('There are no shows available.'))

    # Select all available shows
    shows = source.xpath('//li[contains(@data-filter-options,"'+ url + '")]')

    # Filter the avaiable shows by the choosen channel
    for show in shows:

        show_title = show.xpath('./a/img')[0].get('title')
        show_summary = show.xpath('./div[@class="module-content"]/p')[0].text
        show_thumb = show.xpath('./a/img')[0].get('data-retina-src') # better quality than data-origina-src
        show_id = show.xpath('.//a[contains(@class, "itunes")]')[0].get('href')[-40:][:-4] # we need the guid from the url

        oc.add(TVShowObject(
            key=Callback(GetDirectory, title=show_title, id=show_id),
            rating_key=show_id,
            title=show_title,
            summary=show_summary,
            thumb=Resource.ContentsOfURLWithFallback(show_thumb))
        )

    return oc


####################################################################################################
# List episodes of the selected show
@route(PREFIX + '/directory')
def GetDirectory(title, id, page=1):

    oc = ObjectContainer(title1=L('Title'), title2=title)

    url = API_DIR + id + '&pageNumber=' + str(page)
    try:
        feed = JSON.ObjectFromURL(url, cacheTime=None)
    except Exception as e:
        Log.Error(e)
        return ObjectContainer(header=L('Empty'), message=L('There are no episodes available.'))

    pages = int(feed['maxPageNumber'])
    nextpage = str(int(page) + 1)

    for item in feed['episodes']:

        try:
            item_id = item['assets'][0]['url'][-36:]
        except:
            pass

        url = API_ITEM %item_id

        oc.add(VideoClipObject(
            url = url,
            title = item['title'],
            summary = item['description'],
            thumb = Resource.ContentsOfURLWithFallback(item['imageUrl'])
        ))

    # Add page break
    if page < pages:
        oc.add(NextPageObject(key=Callback(GetDirectory, title=title, id=id, page=nextpage), title=L('MoreItems')))

    return oc
