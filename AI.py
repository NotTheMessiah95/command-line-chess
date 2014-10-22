import sys
from Coordinate import Coordinate as C
from Move import Move
from Piece import Piece
from Board import Board
from MoveNode import MoveNode
from InputParser import InputParser
import copy
import random
from multiprocessing import Queue, Pool, Process


WHITE = True
BLACK = False

class AI :

    depth = 1
    board = None
    side = None
    movesAnalyzed = 0
    

    def __init__(self, board, side, depth) :
        self.board = board
        self.side = side
        self.depth = depth
        self.parser = InputParser(self.board, self.side)



    def getFirstMove(self, side) :
        move = list(self.board.getAllMovesLegal(side))[0]
        return move

    def getAllMovesLegalConcurrent (self, side) :
        p = Pool(8)
        unfilteredMovesWithBoard = [(move, copy.deepcopy(self.board)) for move in self.board.getAllMovesUnfiltered(side)]
        legalMoves = p.starmap(self.returnMoveIfLegal, unfilteredMovesWithBoard)
        p.close()
        p.join()
        return list(filter(None, legalMoves))

    def minChildrenOfNode(self, node) :
        lowestNodes = []
        for child in node.children :
            if not lowestNodes :
                lowestNodes.append(child)
            elif child < lowestNodes[0] :
                lowestNodes = []
                lowestNodes.append(child)
            elif child == lowestNodes[0] :
                lowestNodes.append(child)
        return lowestNodes

    def maxChildrenOfNode(self, node) :
        highestNodes = []
        for child in node.children :
            if not highestNodes :
                highestNodes.append(child)
            elif child < highestNodes[0] :
                highestNodes = []
                highestNodes.append(child)
            elif child == highestNodes[0] :
                highestNodes.append(child)
        return highestNodes

    #def traverseNodeForPointAdvantage(self, node) :
        #nodeSide = board.sideOfMove(node.move)
        #if not node.children :
            #board.makeMove(node.move)
            #pointAdvantage = board.getPointAdvantageOfSide(side)
            #for _ in range(node.depth) :
                #board.undoLastMove()
            #return pointAdvantage

        #child = None
        #if side  == self.side :
            #child = self.maxChildOfNode(node)
        #else :
            #child = self.minChildOfNode(node)

        #board.makeMove(child.move)
        #return traverseNodeForPointAdvantage(self, child)
        
    def getRandomMove(self) :
        legalMoves = list(self.board.getAllMovesLegal(self.side))
        randomMove = random.choice(legalMoves)
        return randomMove

    def generateMoveTree(self) :
        moveTree = []
        for move in self.board.getAllMovesLegal(self.side) :
            moveTree.append(MoveNode(move, [], None))

        for node in moveTree :
            self.board.makeMove(node.move)
            self.populateNodeChildren(node)
            self.board.undoLastMove()
            #for _ in range(self.depth) :
        


        return moveTree


    #def generateNode(self, node) :
        #if node.getDepth() == self.depth :
            #return node
        #move = node.move
        
        #side = self.board.getSideOfMove(move)
        #node.pointAdvantage = self.board.getPointAdvantageOfSide(side)
        #self.board.makeMove(move)
        #for childMove in self.getAllMovesLegal(side) :
            #node.children.append(MoveNode(childMove, [], node))
        #for child in node.children :
            #self.generateNode(child)
            ##if child.children : 
                ##self.board.undoLastMove()
        ##self.board.undoLastMove()

    def populateNodeChildren(self, node) :
        #if self.board.isCheckmate() :
            #node.pointAdvantage = 100
            #return
        node.pointAdvantage = self.board.getPointAdvantageOfSide(self.side)
        node.depth = node.getDepth()
        if node.depth == self.depth :
            return

        side = self.board.currentSide
        
        legalMoves = self.board.getAllMovesLegal(side)
        if not legalMoves :
            if self.board.isCheckmate() :
                node.move.checkmate = True
                node.pointAdvantage = 100
                return
            else :
                node.move.stalemate = True
                return

        for move in legalMoves :
            self.movesAnalyzed += 1
            node.children.append(MoveNode(move, [], node))
            self.board.makeMove(move)
            self.populateNodeChildren(node.children[-1])
            self.board.undoLastMove()

    def getOptimalPointAdvantageForNode(self, node) :
        if node.children:
            for child in node.children :
                child.pointAdvantage = self.getOptimalPointAdvantageForNode(child)

            #If the depth is divisible by 2, it's a move for the AI's side, so return max
            if node.children[0].depth % 2 == 1 :
                return(max(node.children).pointAdvantage)
            else :
                return(min(node.children).pointAdvantage)
        else :

            return node.pointAdvantage



    
    def getBestMove(self) :
        moveTree = self.generateMoveTree()
        bestMoves = self.bestMovesWithMoveTree(moveTree)
        randomBestMove = random.choice(bestMoves)
        randomBestMove.notation = self.parser.notationForMove(randomBestMove)
        return randomBestMove

    def makeBestMove(self) :
        self.board.makeMove(self.getBestMove())
        
    def bestMovesWithMoveTree(self, moveTree) :
        bestMoveNodes = []
        for moveNode in moveTree :
            moveNode.pointAdvantage = self.getOptimalPointAdvantageForNode(moveNode)
            if not bestMoveNodes :
                bestMoveNodes.append(moveNode)
            elif moveNode > bestMoveNodes[0] :
                bestMoveNodes = []
                bestMoveNodes.append(moveNode)
            elif moveNode == bestMoveNodes[0] :
                bestMoveNodes.append(moveNode)
        
        return [node.move for node in bestMoveNodes]

    def traverseTreeForBestMove(self, side, moveTree, layersTraversed, bestMovesFound) :
        if layersLeft < self.depth :
            for move in moveTree :
                board.makeMove(move)
                return traverseTreeForBestMove(moveTree[move], layersLeft+1, bestMoveFound)
        if layersLeft == self.depth :
            for move in moveTree :
                board.makeMove(move)
                pointAdvantage = board.getPointAdvantageOfSide(side)
                previousBestAdvantage = 1
                return move
                
    def isValidMove(self, move, side) :
        for legalMove in self.board.getAllMovesLegal(side) :
            if move == legalMove :
                return True
        return False


    def recursiveMoveFinder(self, moveTree, bestMove) :
        pass



    #def getRandomMoveConcurrent(self, side) :
        #randomMove = random.choice(self.getAllMovesLegalConcurrent(side))
        #return randomMove

    def makeRandomMove(self) :
        moveToMake = self.getRandomMove()
        self.board.makeMove(moveToMake)


if __name__ == "__main__" :
    mainBoard = Board()
    ai = AI(mainBoard, True, 2)
    print(mainBoard)
    ai.makeBestMove()
    print(mainBoard)
    print(ai.movesAnalyzed)
    print(mainBoard.movesMade)

