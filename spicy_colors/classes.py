import math

class Tournament:
    def __init__(self, size):
        self.size = size
        self.pool = []
        self.champion = None
        self.winners = []
        self.versus = []
        self.stage = 1
        self.stages = int(math.log(size, 2))
        self.teamNum = 0
    
    def getPool(self):
        return self.pool

    def addID(self, id):
        self.pool.append(id)

    def createTwo(self, teamNum):
        self.versus = [self.pool[2 * teamNum], self.pool[2 * teamNum + 1]]

    def voteWinner(self, winner):
        winner = self.versus.pop(winner)
        self.winners.append(winner)

    def nextTeam(self):
        if self.teamNum < self.size // 2:
            self.teamNum += 1
            self.createTwo(self.teamNum)

    def nextStage(self):
        self.pool = self.winners
        self.size = len(self.pool)
        self.teamNum = 0
        self.createTwo(self.teamNum)
        self.winners = []
        self.stage += 1

    def isLastStage(self):
        return self.stage == self.stages
            