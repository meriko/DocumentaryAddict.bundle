TITLE  = 'Documentary Addict'
PREFIX = '/video/documentaryaddict'

BASE_URL = 'http://documentaryaddict.com'

ART   = "art-default.jpg"
THUMB = 'icon-default.png'

ITEMS_PER_PAGE = 16

CHOICES = [
    {
        'title':    'Most Viewed',
        'order':    'c_view'
    },
    {
        'title':    'Most Recent',
        'order':    'c_create'
    },
    {
        'title':    'All (A - Z)',
        'order':    'c_name'
    }
]

##########################################################################################
def Start():
    DirectoryObject.thumb = R(THUMB)
    ObjectContainer.art   = R(ART)

    HTTP.CacheTime = CACHE_1HOUR  

##########################################################################################
@handler(PREFIX, TITLE, thumb = THUMB, art = ART)
def MainMenu():
    oc = ObjectContainer(title1 = TITLE)

    for choice in CHOICES:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Items, 
                        title2 = choice['title'], 
                        order = choice['order'],
                    ),
                title = choice['title']
            )
        )
    
    title = "Categories"
    oc.add(
        DirectoryObject(
            key = Callback(Categories, title = title),
            title = title
        )
    )
    
    title = "Search..."
    oc.add(
        InputDirectoryObject(
            key = Callback(Search),
            title = title, 
            prompt = title,
            thumb = R(THUMB)
        )
    )
    
    return oc

##########################################################################################
@route(PREFIX + '/Categories')
def Categories(title):
    oc = ObjectContainer(title2 = title)
    
    pageElement = HTML.ElementFromURL(BASE_URL)
    for item in pageElement.xpath("//*[@itemprop='genre']"):
        title = item.xpath("./text()")[0]
        link = item.xpath("./ancestor::a/@href")[0]
        url = BASE_URL + '/' + link[1:]
    
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        CategoryChoice,
                        title = title,
                        url = url
                    ),
                title = title
            )
        )
    
    return oc
   
##########################################################################################
@route(PREFIX + '/CategoryChoice')
def CategoryChoice(title, url):
    oc = ObjectContainer(title2 = title)
    pageElement = HTML.ElementFromURL(url)
    
    for action in pageElement.xpath("//form/@action"):
        if 'index.php?page=movie&do=category' in action:
            break
    
    if action.startswith("#"):
        link = '/' + action
    else:
        link = '/' + action[1:]
    
    for choice in CHOICES:        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Items,
                        title2 = title,
                        order = choice['order'],
                        link = link
                    ),
                title = choice['title']
            )
        )
    
    return oc 

##########################################################################################
@route(PREFIX + '/Items', page = int)
def Items(title2, order = None, key = None, link = '/index.php?page=movie&do=type&type_id=2&view=thumb', page = 1):
    oc = ObjectContainer(title2 = title2)
    url = BASE_URL + link + '&p=%s' % (page)
    
    if order:
        values = {'order': order}
    else:
        values = {'key': key}
        
    pageElement = HTML.ElementFromURL(url=url, values=values)

    for item in pageElement.xpath("//*[@class='innerLR']//*[@class='col-md-3']"):
        link = item.xpath(".//a/@href")[0].replace("..", "")
        
        title = item.xpath(".//a/@title")[0].strip()
        
        try:
            summary = String.StripTags(item.xpath(".//*[@class='infosml']/text()")[0].strip())

        except:
            try:
                summary = String.StripTags(item.xpath(".//*[@class='caption']//p/text()")[0].strip())
            except:
                summary = None
    
        if summary:
            if 'requires flash' in summary.lower():
                continue

        try:
            thumb = item.xpath(".//img/@data-src")[0]
        except:
            thumb = None

        oc.add(
            VideoClipObject(
                url = BASE_URL + '/' + link,
                title = title,
                summary = summary,
                thumb = thumb
            )
        )

    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = unicode("Couldn't find any content")
        
        return oc
    
    elif len(oc) >= ITEMS_PER_PAGE:
        oc.add(
            NextPageObject(
                key = 
                    Callback(
                        Items,
                        title2 = title2,
                        order = order,
                        key = key,
                        page = page + 1
                    ),
                title = unicode("More...")
            )
        )
    
    return oc

##########################################################################################
@route(PREFIX + '/Search')
def Search(query):
    return Items(
        title2 = 'Results for "%s"' % query,
        link = '/index.php?page=movie&do=search&method=post',
        key = String.Quote(query)
    )
