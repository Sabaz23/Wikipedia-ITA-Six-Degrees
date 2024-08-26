
import requests
import re
from threading import Thread
import threading
from LogHelper import LogHelper
from anytree import Node

URL_PREFIX = "https://it.wikipedia.org"

INVALID_URLS = ['/wiki/Categoria', 
                '/wiki/Aiuto', 
                '/wiki/Discussioni_template', 
                '/wiki/Template', 
                '/wiki/Wikipedia', 
                '/wiki/Speciale', 
                '/wiki/File', 
                '/wiki/Portale', 
                '/wiki/Discussione',
                '/wiki/Pagina_principale']

#Test
sourceUrl = "/wiki/Regia_Marina"
destUrl =  "/wiki/Maarn"

linksToNode = {} #Map from link (str) to Node (tree)

foundDestNode = None


def getValidLinks(url :str) -> list:
    validLinks = []
    requestSuccessed = False
    # catching handing error because of network
    while not requestSuccessed:
        try:
            reqs = requests.get(URL_PREFIX + url)
            requestSuccessed = True
        except:
            pass
    # parsing all the links of the page     
    pattern = "href=\"/wiki/[^\"]*\""
    matches = re.findall(pattern,reqs.text)
    print(reqs.status_code)
    logFile = open("lastResponse.log", "w", encoding="utf-8")
    logFile.write(str(reqs.text))
    logFile.close()
    
    for linkText in matches:
        linkText = linkText.replace("href=\"", "")
        linkText = linkText.replace("\"", "")
        # A link might not have an href
        if linkText is None:
            continue 
        # Rejecting the links that are not valid for the game
        isLinkInvalid = False
        for i_u in INVALID_URLS:
            if linkText.startswith(i_u):
                isLinkInvalid = True
                break
        if isLinkInvalid:
            continue
        # if starts with /wiki it is valid
        if linkText.startswith("/wiki/"):
            validLinks.append(linkText)
    return validLinks


def addNodeToTree(srcUrl :str, parentNode :Node= None) -> Node:
    if srcUrl in linksToNode:
        return None
    node = Node(srcUrl,parentNode)
    linksToNode[srcUrl] = node
    return node


def exploreWikipedia(originUrl :str, destinUrl :str) -> Node:
    iterationStep = 0
    loadedPages = 0
    linksToNode.clear()
    treeRoot = addNodeToTree(originUrl)
    nextNodes = [treeRoot]
    while True:
        if foundDestNode:
            break
        currentNodes = nextNodes.copy()
        nextNodes = []
        logHelper = LogHelper(iterationStep, currentNodes, linksToNode, loadedPages)
        threads = []
        for _ in range(257):
            thread = Thread(target=exploreAvailableNodes, args=[logHelper, destinUrl, currentNodes, nextNodes])
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread :Thread= thread
            thread.join()
        iterationStep += 1


def exploreAvailableNodes(logHelper :LogHelper, destinUrl :str, currentNodes :list, nextNodes :list):
    global foundDestNode
    while True:
        # If another thread found the node, interrupt this thread
        if foundDestNode:
            #print("DestNode Trovato! Termino esecuzione thread - " + threading.current_thread().name)
            return
        # Another thread might have emptied the list, if that is the case, interrupt this thread
        try:
            currNode :Node= currentNodes.pop()
        except IndexError:
            return
        # Load a new page corresponding to the link
        tempLinks = getValidLinks(currNode.name)
        logHelper.loadedPages += 1
        # Check all the links of the page
        for link in tempLinks:
            node = addNodeToTree(link,currNode)
            if node is None:
                continue
            if link != destinUrl:
                nextNodes.append(node)
                logHelper.printLogs()
                continue
            foundDestNode = node
            return
            

def recostructPathToDest(destNode :Node) -> list:
    newPath = []
    node = destNode
    while True:
        if node is None:
            return newPath
        newPath.append(node.name)
        node = node.parent


exploreWikipedia(sourceUrl, destUrl)
print(recostructPathToDest(foundDestNode))