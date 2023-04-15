import random
from copy import deepcopy

import pygame
import pymsgbox
import numpy as np


class pathFinder:
    def __init__(self, resolution):
        self.isPathDrawingFinish = True
        self.isPathFind = False
        self.isButtonStartPressed = False
        self.listNode = {}
        self.obstaclePos = []
        self.sourcePos = None
        self.visitedPath = []
        self.source = 2
        self.destination = 3
        self.obstacle = 4
        self.path = 5
        self.isObstaclePuted = False
        self.isSourcePuted = False
        self.isDestinationPuted = False
        self.distance = 10000
        pygame.init()
        self.windowBackgroundColor = "gray"
        self.isWindowOpen = True
        self.resolution = resolution
        self.window = pygame.display.set_mode(self.resolution, pygame.RESIZABLE)
        self.gridCellSize = 10
        self.gridSupportSupport = pygame.Rect(0, 0, self.resolution[0], self.resolution[1] - 100)
        self.gridSize = [self.gridSupportSupport.height // self.gridCellSize,
                         self.gridSupportSupport.height // self.gridCellSize]
        self.gridMatrix = np.zeros(self.gridSize)
        self.buttonGridSize = pygame.Rect(self.resolution[0] - 100, (100 - 25) / 2 + self.gridSupportSupport.height, 50,
                                          25)
        self.buttonGridPause = pygame.Rect(self.resolution[0] - 200, (100 - 25) / 2 + self.gridSupportSupport.height,
                                           50, 25)
        self.buttonGridPlay = pygame.Rect(self.resolution[0] - 300, (100 - 25) / 2 + self.gridSupportSupport.height, 50,
                                          25)
        self.buttonGridClear = pygame.Rect(self.resolution[0] - 400, (100 - 25) / 2 + self.gridSupportSupport.height,
                                           50, 25)
        self.buttonGridObstaclesGenerator = pygame.Rect(self.resolution[0] - 525,
                                                        (100 - 25) / 2 + self.gridSupportSupport.height,
                                                        75, 25)
        self.gridSupport = pygame.Rect((self.gridSupportSupport.width - self.gridSize[0] * self.gridCellSize) / 2,
                                       (self.gridSupportSupport.height - self.gridSize[1] * self.gridCellSize) / 2,
                                       self.gridSize[0] * self.gridCellSize, self.gridSize[1] * self.gridCellSize)
        self.font = pygame.font.SysFont("arial", 15)
        self.djikstraMatrix = []
        self.neightborDico = {}
        self.neightborDico2 = {}
        self.weightDico = {}
        self.precNode = []
        self.nextNode = []
        pygame.display.set_caption("pathFInder")

        self.resizeFont = self.font.render("dim", True, "black")
        self.pauseFont = self.font.render("pause", True, "black")
        self.playFont = self.font.render("play", True, "black")
        self.clearFont = self.font.render("clear", True, "black")
        self.obstacleFont = self.font.render("gen-wall", True, "black")

        self.pauseFontPos = [(self.buttonGridPause.width - self.pauseFont.get_width()) / 2 + self.buttonGridPause.x,
                             (self.buttonGridPause.height - self.pauseFont.get_height()) / 2 + self.buttonGridPause.y]
        self.playFontPos = [(self.buttonGridPlay.width - self.playFont.get_width()) / 2 + self.buttonGridPlay.x,
                            (self.buttonGridPlay.height - self.playFont.get_height()) / 2 + self.buttonGridPlay.y]
        self.clearFontPos = [(self.buttonGridClear.width - self.clearFont.get_width()) / 2 + self.buttonGridClear.x,
                             (self.buttonGridClear.height - self.clearFont.get_height()) / 2 + self.buttonGridClear.y]
        self.resizeFontPos = [(self.buttonGridSize.width - self.resizeFont.get_width()) / 2 + self.buttonGridSize.x,
                              (self.buttonGridSize.height - self.resizeFont.get_height()) / 2 + self.buttonGridSize.y]
        self.obstacleFontPos = [(self.buttonGridObstaclesGenerator.width - self.obstacleFont.get_width()) / 2 + self.buttonGridObstaclesGenerator.x,
                                (self.buttonGridObstaclesGenerator.height - self.obstacleFont.get_height()) / 2 + self.buttonGridObstaclesGenerator.y]

    def main(self):
        while self.isWindowOpen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isWindowOpen = False
                    pygame.quit()
                elif event.type == pygame.VIDEORESIZE:
                    self.resolution = [self.window.get_width(), self.window.get_height()]
                    self.task_after_window_resize()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.buttonGridSize.collidepoint(pygame.mouse.get_pos()):
                        self.resize_grid()
                    elif self.buttonGridPlay.collidepoint(pygame.mouse.get_pos()):
                        self.play()
                    elif self.buttonGridPause.collidepoint(pygame.mouse.get_pos()):
                        self.pause()
                    elif self.buttonGridClear.collidepoint(pygame.mouse.get_pos()):
                        self.clear()
                    elif self.buttonGridObstaclesGenerator.collidepoint(pygame.mouse.get_pos()):
                        self.obstacleGenerate()
                    elif self.gridSupport.collidepoint(pygame.mouse.get_pos()):
                        x = pygame.mouse.get_pos()[0]
                        y = pygame.mouse.get_pos()[1]
                        if not self.isSourcePuted:
                            self.gridMatrix[(y - self.gridSupport.y) // self.gridCellSize][
                                (x - self.gridSupport.x) // self.gridCellSize] = self.source
                            self.sourcePos = ((y - self.gridSupport.y) // self.gridCellSize,
                                              (x - self.gridSupport.x) // self.gridCellSize)
                            self.isSourcePuted = True
                        elif not self.isDestinationPuted:
                            self.gridMatrix[(y - self.gridSupport.y) // self.gridCellSize][
                                (x - self.gridSupport.x) // self.gridCellSize] = self.destination
                            self.obstaclePos = [(y - self.gridSupport.y) // self.gridCellSize,
                                                (x - self.gridSupport.x) // self.gridCellSize]
                            self.isDestinationPuted = True
                            self.destinationPos = ((y - self.gridSupport.y) // self.gridCellSize,
                                                   (x - self.gridSupport.x) // self.gridCellSize)
                        elif not self.isObstaclePuted:
                            self.gridMatrix[(y - self.gridSupport.y) // self.gridCellSize, (
                                    x - self.gridSupport.x) // self.gridCellSize] = self.obstacle

            if self.isWindowOpen:
                self.window.fill(self.windowBackgroundColor)

                if self.isButtonStartPressed:
                    if not self.isPathFind:
                        self.djikstra()
                    if not self.isPathDrawingFinish:
                        self.draw_path()

                self.draw_element()

                pygame.display.flip()

    def initialize(self):
        self.neightborDico.clear()
        for i in range(self.gridMatrix.shape[0]):
            for j in range(self.gridMatrix.shape[1]):
                if not self.gridMatrix[i][j] == 4:
                    self.neightborDico[(i, j)] = [[], self.distance]
                    if self.gridSupport.collidepoint([j * self.gridCellSize + self.gridSupport.x,
                                                      (i - 1) * self.gridCellSize + self.gridSupport.y]) and not \
                            self.gridMatrix[i - 1][j] == 4:
                        self.neightborDico[(i, j)][0].append((i - 1, j))
                    if self.gridSupport.collidepoint([(j + 1) * self.gridCellSize + self.gridSupport.x,
                                                      i * self.gridCellSize + self.gridSupport.y]) and not \
                            self.gridMatrix[i][j + 1] == 4:
                        self.neightborDico[(i, j)][0].append((i, j + 1))
                    if self.gridSupport.collidepoint([(j) * self.gridCellSize + self.gridSupport.x,
                                                      (i + 1) * self.gridCellSize + self.gridSupport.y]) and not \
                            self.gridMatrix[i + 1][j] == 4:
                        self.neightborDico[(i, j)][0].append((i + 1, j))
                    if self.gridSupport.collidepoint([(j - 1) * self.gridCellSize + self.gridSupport.x,
                                                      i * self.gridCellSize + self.gridSupport.y]) and not \
                            self.gridMatrix[i][j - 1] == 4:
                        self.neightborDico[(i, j)][0].append((i, j - 1))
        self.neightborDico[self.sourcePos][1] = 0
        self.nextNode = self.sourcePos

    def draw_element(self):
        pygame.draw.rect(self.window, "wheat", self.gridSupportSupport)
        pygame.draw.rect(self.window, (230, 230, 230), self.gridSupport)
        pygame.draw.rect(self.window, "white", self.buttonGridSize)
        pygame.draw.rect(self.window, "white", self.buttonGridPlay)
        pygame.draw.rect(self.window, "white", self.buttonGridPause)
        pygame.draw.rect(self.window, "white", self.buttonGridClear)
        pygame.draw.rect(self.window, "white", self.buttonGridObstaclesGenerator)
        for i in range(self.gridMatrix.shape[0]):
            for j in range(self.gridMatrix.shape[1]):
                if self.gridMatrix[i][j] == self.destination:
                    pygame.draw.rect(self.window, "green", (
                        j * self.gridCellSize + self.gridSupport.x, i * self.gridCellSize + self.gridSupport.y,
                        self.gridCellSize, self.gridCellSize))
                if self.gridMatrix[i][j] == self.source:
                    pygame.draw.rect(self.window, "red", (
                        j * self.gridCellSize + self.gridSupport.x, i * self.gridCellSize + self.gridSupport.y,
                        self.gridCellSize, self.gridCellSize))
                if self.gridMatrix[i][j] == self.obstacle:
                    pygame.draw.rect(self.window, "black", (
                        j * self.gridCellSize + self.gridSupport.x, i * self.gridCellSize + self.gridSupport.y,
                        self.gridCellSize, self.gridCellSize))
                if self.gridMatrix[i][j] == self.path:
                    pygame.draw.rect(self.window, "brown", (
                        j * self.gridCellSize + self.gridSupport.x, i * self.gridCellSize + self.gridSupport.y,
                        self.gridCellSize, self.gridCellSize))
                if self.gridMatrix[i][j] == 1:
                    pygame.draw.rect(self.window, (150, 150, 255), (
                        j * self.gridCellSize + self.gridSupport.x, i * self.gridCellSize + self.gridSupport.y,
                        self.gridCellSize, self.gridCellSize))
        for i in range(self.gridSupport.width // self.gridCellSize + 1):
            pygame.draw.line(self.window, "black", (self.gridSupport.x + i * self.gridCellSize, self.gridSupport.y),
                             (self.gridSupport.x + i * self.gridCellSize, self.gridSupport.y + self.gridSupport.height))
        for i in range(self.gridSupport.height // self.gridCellSize + 1):
            pygame.draw.line(self.window, "black", (self.gridSupport.x, self.gridSupport.y + i * self.gridCellSize),
                             (self.gridSupport.x + self.gridSupport.width, self.gridSupport.y + i * self.gridCellSize))
        self.window.blit(self.pauseFont, self.pauseFontPos)
        self.window.blit(self.playFont, self.playFontPos)
        self.window.blit(self.clearFont, self.clearFontPos)
        self.window.blit(self.resizeFont, self.resizeFontPos)
        self.window.blit(self.obstacleFont, self.obstacleFontPos)

    def task_after_window_resize(self):
        self.gridSupportSupport.width = self.resolution[0]
        self.gridSupportSupport.height = self.resolution[1] - 100
        self.buttonGridSize = pygame.Rect(self.resolution[0] - 100, (100 - 25) / 2 + self.gridSupportSupport.height, 50,
                                          25)
        self.buttonGridPause = pygame.Rect(self.resolution[0] - 200, (100 - 25) / 2 + self.gridSupportSupport.height,
                                           50, 25)
        self.buttonGridPlay = pygame.Rect(self.resolution[0] - 300, (100 - 25) / 2 + self.gridSupportSupport.height, 50,
                                          25)
        self.buttonGridClear = pygame.Rect(self.resolution[0] - 400, (100 - 25) / 2 + self.gridSupportSupport.height,
                                           50, 25)
        self.gridSize = [self.gridSupportSupport.height // self.gridCellSize,
                         self.gridSupportSupport.height // self.gridCellSize]
        self.gridSupport.center = self.gridSupportSupport.center
        self.pauseFontPos = [(self.buttonGridPause.width - self.pauseFont.get_width()) / 2 + self.buttonGridPause.x,
                             (self.buttonGridPause.height - self.pauseFont.get_height()) / 2 + self.buttonGridPause.y]
        self.playFontPos = [(self.buttonGridPlay.width - self.playFont.get_width()) / 2 + self.buttonGridPlay.x,
                            (self.buttonGridPlay.height - self.playFont.get_height()) / 2 + self.buttonGridPlay.y]
        self.clearFontPos = [(self.buttonGridClear.width - self.clearFont.get_width()) / 2 + self.buttonGridClear.x,
                             (self.buttonGridClear.height - self.clearFont.get_height()) / 2 + self.buttonGridClear.y]
        self.resizeFontPos = [(self.buttonGridSize.width - self.resizeFont.get_width()) / 2 + self.buttonGridSize.x,
                              (self.buttonGridSize.height - self.resizeFont.get_height()) / 2 + self.buttonGridSize.y]

    def resize_grid(self):
        try:
            x = int(pymsgbox.prompt('entrer le bombre de ligne'))
            y = int(pymsgbox.prompt('entrer le nombre de colonne'))
            if 0 < y < self.gridSupportSupport.width // self.gridCellSize and 0 < x < self.gridSupportSupport.height // self.gridCellSize:
                self.gridSize[0] = x
                self.gridSize[1] = y
                self.gridMatrix = np.zeros((x, y))
                self.gridSupport.size = [self.gridMatrix.shape[1] * self.gridCellSize,
                                         self.gridMatrix.shape[0] * self.gridCellSize]
                self.gridSupport.center = self.gridSupportSupport.center
                self.isObstaclePuted = False
                self.isSourcePuted = False
                self.isDestinationPuted = False
        except:
            pass

    def play(self):
        if self.isSourcePuted:
            self.isObstaclePuted = True
            self.initialize()
            self.isButtonStartPressed = True
            self.precNode = self.sourcePos
            self.listNode[self.sourcePos] = 0
            self.neightborDico2 = deepcopy(self.neightborDico)

    def pause(self):
        self.isButtonStartPressed = True
        print("pause")

    def clear(self):
        self.gridMatrix = np.zeros(self.gridSize)
        self.djikstraMatrix = []
        self.neightborDico.clear()
        self.weightDico.clear()
        self.neightborDico2.clear()
        self.isObstaclePuted = False
        self.isSourcePuted = False
        self.isDestinationPuted = False
        self.isButtonStartPressed = False
        self.isPathDrawingFinish = True
        self.isPathFind = False
        self.listNode.clear()

    def djikstra(self):
        try:
            dicoNeighborWeight = {}
            for link in self.neightborDico[self.precNode][0]:
                if self.neightborDico[self.precNode][1] + 1 < self.neightborDico[link][1]:
                    self.neightborDico[link][1] = self.neightborDico[self.precNode][1] + 1
                    self.neightborDico2[link][1] = self.neightborDico[self.precNode][1] + 1
            for link in self.neightborDico[self.precNode][0]:
                dicoNeighborWeight[link] = self.neightborDico[link][1]
            self.nextNode = min(dicoNeighborWeight, key=dicoNeighborWeight.get)
            self.neightborDico[self.precNode][0].remove(self.nextNode)
            self.neightborDico[self.nextNode][0].remove(self.precNode)
            if self.nextNode == self.destinationPos:
                self.isPathFind = True
                self.isPathDrawingFinish = False
                self.precNode = self.destinationPos
            if not self.isPathFind:
                self.gridMatrix[self.nextNode] = 1
                self.listNode[self.nextNode] = self.neightborDico[self.nextNode][1]
                tmpDic = deepcopy(self.listNode)
                for pos in tmpDic:
                    if len(self.neightborDico[pos][0]) == 0:
                        self.listNode.pop(pos)
                self.precNode = min(self.listNode, key=self.listNode.get)
        except ValueError:
            self.isPathFind = True

    def draw_path(self):
        if not self.isPathDrawingFinish:
            dicoNeighborWeight = {}
            for link in self.neightborDico2[self.precNode][0]:
                dicoNeighborWeight[link] = self.neightborDico2[link][1]
            self.nextNode = min(dicoNeighborWeight, key=dicoNeighborWeight.get)
            self.neightborDico2[self.precNode][0].remove(self.nextNode)
            self.neightborDico2[self.nextNode][0].remove(self.precNode)
            if self.nextNode == self.sourcePos:
                self.isPathDrawingFinish = True
            else:
                self.gridMatrix[self.nextNode] = self.path
            self.precNode = self.nextNode

    def obstacleGenerate(self):
        x = int(pymsgbox.prompt('entrer le bombre brique'))
        i = self.random_xy()[0]
        j = self.random_xy()[1]
        for k in range(x):
            while self.gridMatrix[i][j] == 4:
                i = self.random_xy()[0]
                j = self.random_xy()[1]
            self.gridMatrix[i][j] = 4

    def random_xy(self):
        return random.randint(0, self.gridMatrix.shape[0]-1), random.randint(0, self.gridMatrix.shape[1]-1)


if __name__ == "__main__":
    pathFinder((700, 650)).main()
