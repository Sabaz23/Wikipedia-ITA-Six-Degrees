import psutil
from threading import Semaphore

PROCESS = psutil.Process()
MB = 1024*1024

class LogHelper:
    def __init__(self, iterationStep, stepNodes, linkToNode, loadedPages):
        # The current iteration step (number of clicks)
        self.iterationStep = iterationStep
        # The total number of loaded web pages
        self.loadedPages = loadedPages
        # The dictionary that maps links to nodes
        self.linkToNode = linkToNode
        self.stepNodes = stepNodes
        self.stepMaxNodes = len(stepNodes)
        # Semaphore for logging without threading problems
        self.printSemaphore = Semaphore(1)

    def printLogs(self):
        if len(self.linkToNode)%100 == 0:
            self.printSemaphore.acquire()
            print("-------------- Added new 100 nodes --------------")
            print("Missing "+str(len(self.stepNodes))+"/"+str(self.stepMaxNodes)+" for step "+str(self.iterationStep))
            print("Total nodes in map: " + str(len(self.linkToNode)))
            print("Total pages visited: " + str(self.loadedPages))
            print("Memory usage: "+str(PROCESS.memory_info().rss / MB)+"MB")
            self.printSemaphore.release()