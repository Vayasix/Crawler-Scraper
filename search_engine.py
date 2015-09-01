from pyquery import PyQuery as pq
from lxml import etree
from urllib import urlopen

#Simple page ranking algorithm.
#calc the weight of each page url
def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d * (ranks[node]/len(graph[node]))
            newranks[page] = newrank
        ranks = newranks
    return ranks

def generate_pyquery_object(page_url):
    Obj = pq("<html></html>")
    Obj = pq(etree.fromstring("<html></html>"))
    Obj = pq(url=page_url)
    Obj = pq(url=page_url, opener=lambda url, **kw: urlopen(url).read())
    #Obj = pq(filename=path_to_html_file)
    return Obj


def crawl_web(seed): # returns index, graph of inlinks
    tocrawl = [seed]
    crawled = []
    graph = {}  # <url>, [list of pages it links to]
    index = {} 
    while tocrawl: 
        page = tocrawl.pop()
        print tocrawl
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            union(tocrawl, outlinks)
            crawled.append(page)
    return index, graph


def get_page(url):
    if url in cache:
        return cache[url]
    else:
        return None

def get_all_links(content):
    links = []
    html = pq(content)
    a_tags = html.find('a')
    for a_tag in a_tags:
        url = pq(a_tag).attr('href')
        if url:
            links.append(url)
    return links


def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    if content == None: return
    content = content.text()
    words = content.split()
    for word in words:
        add_to_index(index, word, url)
        
def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

def parse_html(page_url):
    return pq(url = page_url)

""" demo """
#you can insert your own links into page_urls
page_urls = ['http://snap.stanford.edu', 'http://snap.stanford.edu/links.html']
cache = {}
for page_url in page_urls:
    html_pqObj = parse_html(page_url)
    cache[page_url] = html_pqObj

seed_page_url = page_urls[0]
index, graph = crawl_web(seed_page_url)
ranks = compute_ranks(graph)
print ranks

