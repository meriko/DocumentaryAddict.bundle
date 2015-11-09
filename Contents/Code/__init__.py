TITLE  = 'Documentary Addict'
PREFIX = '/video/documentaryaddict'

BASE_URL = 'http://documentaryaddict.com'

ART   = "art-default.jpg"
THUMB = 'icon-default.png'

ITEMS_PER_PAGE = 16

CHOICES = [
    {
        'title':    'Most Viewed',
        'order':    'C_View'
    },
    {
        'title':    'Most Recent',
        'order':    'created_at'
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
    
    pageElement = HTML.ElementFromURL(BASE_URL + '/films')
    for item in pageElement.xpath("//*[@id='q_FK_CategoryID_eq']//option"):
        try:
            category_id = item.xpath("./@value")[0]
            title = item.xpath("./text()")[0]
        except:
            continue
        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        CategoryChoice,
                        title = title,
                        category_id = category_id
                    ),
                title = title
            )
        )
    
    return oc
   
##########################################################################################
@route(PREFIX + '/CategoryChoice')
def CategoryChoice(title, category_id):
    oc = ObjectContainer(title2 = title)
    
    for choice in CHOICES:        
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        Items,
                        title2 = title,
                        order = choice['order'],
                        category_id = category_id
                    ),
                title = choice['title']
            )
        )
    
    return oc 

##########################################################################################
@route(PREFIX + '/Items', page = int)
def Items(title2, order = '', key = '', category_id = '', page = 1):
    oc = ObjectContainer(title2 = title2)
    
    if order and not category_id:
        url = BASE_URL + '/films?page=%s&%s=%s+desc' % (page, String.Quote('q[s]'), order)
    else:
        url = BASE_URL + '/films?commit=Search&page=%s&%s=%s&%s=%s&%s=%s+desc&utf8=✓' % (page, String.Quote('q[C_Name_cont]'), String.Quote(key), String.Quote('q[FK_CategoryID_eq]'), category_id, String.Quote('q[s]'), order)
        
    pageElement = HTML.ElementFromURL(url)

    for item in pageElement.xpath("//*[contains(@class, 'widget-film')]"):
        url = item.xpath(".//a/@href")[0]
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
            thumb = item.xpath(".//img/@src")[0]
        except:
            thumb = None

        oc.add(
            VideoClipObject(
                url = url,
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
                        category_id = category_id,
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
        key = String.Quote(query)
    )
