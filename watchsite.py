#!/usr/bin/python 

import urllib2
import xml.etree.ElementTree as etree
import re

class RedirectOccured(Exception):
    '''Exception class for the url given by the user resolve in a redirection'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getpage(url):
    '''Used to open html pages raise exception if a redirection occured'''
    page = urllib2.urlopen(url) 
    if url != page.geturl():
        raise RedirectOccured(page.geturl())
    else:
        return page

def getsites(path):
    '''Get the websites the user want to check'''
    root = etree.fromstring(file(path).read())
    listSite = root.findall('site')

    sites = []
    for site in listSite:
        disabled = site.find('disabled').text
        if disabled == '1': # no need to get disabled websites
            continue

        sitename = site.find('sitename').text # arbitrary naming the website
        url = site.find('url').text # url of the website
        checks = {'text':set(), 'image':set()} # list of constraints we will have to look to
        
        for constraint in site.getiterator('rule'):
            if constraint.attrib['type'] == 'text':
                checks['text'].add(constraint.text.strip(' ').strip('\n').strip(' '))
            if constraint.attrib['type'] == 'image':
                checks['image'].add(constraint.text.strip(' ').strip('\n').strip(' '))
        sites.append({'disabled':disabled, 'sitename':sitename, 'url':url, 'checks':checks})

    return sites
    

def handle_text(page, texts):
    '''Function handling text type content'''
    content = page.read()
    for text in texts:
        if not re.search(text, content):  
            return False
    return True
    

def checkpage(page, checks):
    '''Check whether the page pass all the users conditions'''
    if checks['text']: # we have text to find !
        if not handle_text(page, checks['text']):
            return False
    return True

if __name__ == '__main__':
    sites = getsites('./sites.xml')
    for site in sites:
        try:
            page = getpage(site['url'])
            if checkpage(page, site['checks']):
                print '%s : Good' % site['sitename']
            else:
                print '%s : Fails' % site['sitename'] # add an option to send an email or something
        except RedirectOccured as e:
            print 'We have been redirected to %s' % e
        except urllib2.URLError:
            print 'Error occured page not found'
