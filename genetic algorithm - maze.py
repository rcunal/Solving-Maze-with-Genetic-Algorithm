import pygame
import random
import numpy as np
import operator
import time
import timeit

pygame.init()


class Agent:  # her bir bireyi temsil eden class
    def __init__(self, dnaSize):  # dnaSize ile dna boyutu verilerek olusuyor
        self.dnaSize = dnaSize
        self.dna = list()
        self.distance = 0.
        self.X = 1  # baslangic pozisyonu 1
        self.Y = 1  # baslangic pozisyonu 1
        self.die = False  # hayatta
        self.moveCountforAgent = 0  # bireyin kac adim attigini tutan degisken
        self.path = list()  # bireyin gittigi yolun tutuldugu liste
        self.fitness = 0  # fitness functiondan donen degerin tutuldugu degisken
        self.useless = 0  # fitness function icin gerekli useless ve usefull degiskeni
        self.usefull = 0

        for i in range(self.dnaSize):  # birey oluşturulduğunda dnasını random oluşturan loop
            if i != 0:  # ancak ilk dna dışındaki dna kısımlarında sag-sol , sol-sag , yukarı aşağı , aşağı yukarı tekrarı etmemesi için kontrol ediliyor
                randNumber = random.randrange(1, 5)
                while abs(self.dna[i - 1] - randNumber) == 2:
                    randNumber = random.randrange(1, 5)
                self.dna.append(randNumber)
            else:
                self.dna.append(random.randrange(1, 5))


class Simulation:  # simulasyon classı
    def __init__(self, rowCount, columnCount, obstacleCount, popSize, mutationRate, dnaSize, maze,
                 pathColor):  # satır,sütun, engel sayısı , populasyon sayısı, mutasyon degeri, labirent ve yol rengi
        self.rowCount = rowCount  # parametreleri alan simulasyon
        self.columnCount = columnCount
        self.obstacleCount = obstacleCount
        self.popSize = popSize
        self.dnaSize = dnaSize
        self.mutationRate = mutationRate
        self.found = False  # ilk olusturuldugunda daha yol bulunmadığı için false
        self.livingCount = popSize
        self.generationCount = 0  # generation sayısını tutan değişken
        self.foundAgent = Agent(dnaSize)
        self.bestAgent = Agent(dnaSize)
        self.total = 0  # fitness functionı normalize etmek için bütün distanceların toplamını tutan total değişkeni
        self.pathColor = pathColor

        self.width = 600  # pygame window için width ve height değişkeni
        self.height = 600

        self.cellWidth = self.width / self.columnCount  # her bir hücrenin eni
        self.cellHeight = self.height / self.rowCount  # her bir hücrenin boyu

        self.start = 1, 1
        self.finish = self.columnCount - 2, self.rowCount - 2

        self.maze = maze  # aynı maze'de birkaç kez simülasyon döndürebilmek için maze'i sim'in dışında oluşturup burada eşitlememiz gerekti

        self.maze[self.start] = 2  # start pozisyonuna 2
        self.maze[self.finish] = 3  # finish pozisyonuna 3

        self.population = list()
        self.screen = pygame.display.set_mode((self.width, self.height))

        for i in range(self.popSize):  # popülasyon sayısı kadar birey oluşturuluyor
            agent = Agent(self.dnaSize)
            self.population.append(agent)  # population listesine ekleniyor

    def drawMaze(self):  # maze'in renklendirilme fonksiyonu
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (0, 255, 0),
                         (1 * self.cellWidth, 1 * self.cellHeight, self.cellWidth, self.cellHeight))
        pygame.draw.rect(self.screen, (0, 255, 0),
                         (
                             (self.rowCount - 2) * self.cellWidth, (self.columnCount - 2) * self.cellHeight,
                             self.cellWidth,
                             self.cellHeight))

        for i in range(self.rowCount):
            for j in range(self.columnCount):
                if self.maze[i][j] == 1:  # 1 engeller için
                    pygame.draw.rect(self.screen, (255, 0, 0),
                                     (j * self.cellWidth, i * self.cellHeight, self.cellWidth, self.cellHeight))
                elif self.maze[i][j] == 4:  # 4 ise bulunan yolun çizimi için
                    pygame.draw.rect(self.screen, self.pathColor,
                                     (j * self.cellWidth, i * self.cellHeight, self.cellWidth, self.cellHeight), 3)

    def changeMaze(self):  # maze'de yol bulunduktan sonra bireyin dolaştığı yolları 4 yaparak çizimi sağlanıyor
        for i in range(len(self.foundAgent.path)):
            self.maze[self.foundAgent.path[i][1], self.foundAgent.path[i][0]] = 4

        self.drawMaze()
        self.displayHelper()

    def reChangeMaze(
            self):  # aynı mazede deneme yapmak istediğimiz için gösterdikten sonra eski haline getirmek için kullanılan fonksiyon
        for i in range(len(self.foundAgent.path)):
            self.maze[self.foundAgent.path[i][1], self.foundAgent.path[i][0]] = 0

        self.drawMaze()
        self.displayHelper()

    def displayHelper(self):  # pygame windowda gözüken living count ve generation yazıları için kullanılan fonksiyon
        test2 = myFont.render(str(self.livingCount), 1, (255, 255, 255))
        test3 = myFont.render(str(self.generationCount), 1, (255, 255, 255))
        self.screen.blit(test, (420, 10))
        self.screen.blit(test2, (560, 10))
        self.screen.blit(test4, (50, 10))
        self.screen.blit(test3, (140, 10))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

    def drawOnlyBest(self):  # ödevde istenilen en iyi yolu çizen fonksiyon

        self.screen.fill((0, 0, 0))
        self.drawMaze()
        for pos in self.bestAgent.path:
            pygame.draw.rect(self.screen, self.pathColor,
                             (pos[0] * self.cellWidth, pos[1] * self.cellHeight, self.cellWidth,
                              self.cellHeight), 1)
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.bestAgent.X * self.cellWidth, self.bestAgent.Y * self.cellHeight, self.cellWidth,
                          self.cellHeight), 1)
        self.displayHelper()

    def move(self, moveCount):  # bireylerin adım adım dnasına göre hangi yöne gitmesi gerektiğini bulan fonksiyon
        move_x = [-1, 0, 1, 0]
        move_y = [0, -1, 0, 1]
        for agent in self.population:
            if not agent.die:  # eğer birey ölmemişse
                tempX, tempY = agent.X + move_x[agent.dna[moveCount] - 1], agent.Y + move_y[agent.dna[moveCount] - 1]
                if self.maze[tempY][tempX] != 1:  # eğer gideceği yolda duvar yoksa
                    agent.X, agent.Y = tempX, tempY
                    agent.moveCountforAgent += 1  # bireyin adım sayısının arttırımı
                    agent.path.append([agent.X, agent.Y])
                    if moveCount < agent.dnaSize - 1:
                        if abs(agent.dna[moveCount] - agent.dna[moveCount + 1]) == 2:
                            agent.useless += 1  # yaptığı gereksiz hamlelere göre uselessı artıyor
                    if agent.dna[moveCount] == 3 or agent.dna[moveCount] == 4:
                        agent.usefull += 1  # hedefe yaklaştıran ( aşağı veya sağa) hamle sayısına göre usefullu artıyor
                else:  # duvar varsa birey ölür
                    agent.die = True
                    agent.dna[agent.moveCountforAgent] = random.randrange(1,
                                                                          5)  # birey duvara çarptığında o andaki dnasını değiştirerek daha kolay bulunması hedefleniyor
                    self.livingCount -= 1  # yaşayan birey sayısı azaltılır

            if agent.X == self.finish[0] and agent.Y == self.finish[0]:  # eğer yol bulunursa
                self.found = True
                stop = timeit.default_timer()
                time = stop - start
                print("Time:" + str(time))
                self.foundAgent = agent
                print(self.foundAgent.dna)

    def crossOver(self, dna1, dna2):  # crossover fonksiyonu
        child = Agent(self.dnaSize)
        for i in range(self.dnaSize):
            if random.uniform(0,
                              1) > self.mutationRate:  # eğer mutasyona uğramazsa anne ve babadan yarı yarıya rastgele olarak dnalar alınıyor
                if random.randrange(0, 2) == 0:
                    child.dna[i] = dna1[i]
                else:
                    child.dna[i] = dna2[i]
            else:  # mutasyona uğrarsa random
                if i != 0:
                    randNumber = random.randrange(1, 5)
                    while abs(child.dna[i - 1] - randNumber) == 2:
                        randNumber = random.randrange(1, 5)
                    child.dna[i] = randNumber
                else:
                    child.dna[i] = random.randrange(1, 5)

        return child

    def fitness(self):  # bireylerin fitness sayısının hesabını yapan fonksiyon
        for agent in self.population:
            s = (agent.X - self.start[0] + agent.Y - self.start[1])
            f = (self.finish[0] - agent.X + self.finish[1] - agent.Y + 1)

            agent.distance += (s / pow(1.1, f)) * 1000 + 5 + s - (len(agent.path) / agent.dnaSize) - (
                        agent.useless / agent.dnaSize) + (agent.usefull / agent.dnaSize)
            if agent.die == True:
                agent.distance -= 1

            self.total += agent.distance
        maximum = -1
        for agent in self.population:
            agent.fitness = agent.distance / self.total
            if (maximum < agent.fitness):
                maximum = agent.fitness
        self.total = 0

    def newPop(self, generationCount):  # yeni jenerasyonu üreten fonksiyon

        self.fitness()
        popv2 = list()
        self.generationCount = generationCount

        fitnessList = list()
        for i in range(self.popSize):
            fitnessList.append(self.population[i].fitness)

        sortedPopulation = sorted(self.population, key=operator.attrgetter('fitness'), reverse=True)
        self.livingCount = self.popSize
        bestResult = sortedPopulation[0].distance
        self.bestAgent = sortedPopulation[0]

        for i in range(1):  # en iyi score üreten elemanlar gen havuzunda tutularak bir sonraki jenerasyona katılıyor
            best = sortedPopulation[i]
            best.X = 1
            best.Y = 1
            best.die = False
            best.distance = 0.
            best.moveCountforAgent = 0
            best.useless = 0
            best.usefull = 0
            best.path.clear()
            popv2.append(best)

        for i in range(self.popSize - 1):  # burada ise jenerasyonun diğer elemanları üretiliyor
            p1index = np.random.choice(self.popSize, 1, p=fitnessList)[
                0]  # parentlar fitness fonksiyonundan dönen değerlerin ağırlıklarına göre seçiliyor
            p2index = np.random.choice(self.popSize, 1, p=fitnessList)[0]
            parent1 = self.population[p1index]
            parent2 = self.population[p2index]

            while parent2 == parent1:  # aynı parent olmaması için kullanılan döngü
                p2index = np.random.choice(self.popSize, 1, fitnessList)[0]
                parent2 = self.population[p2index]

            dna1 = parent1.dna
            dna2 = parent2.dna
            new = self.crossOver(dna1, dna2)
            popv2.append(new)

        print(' Current Leader Distance: {:.2f}'.format(bestResult))

        self.population.clear()
        self.population = popv2.copy()
        popv2.clear()


def buildMaze(rowCount, columnCount,
              obstacleCount):  # maze oluşturan fonksiyon, satır, sutun ve engel sayısı alıyor parametre olarak
    maze = np.zeros([rowCount, columnCount])  # önce hepsi 0 yapılıyor
    for i in range(rowCount):  # duvarlar 1
        maze[0, i] = 1
        maze[columnCount - 1, i] = 1
        maze[i, 0] = 1
        maze[i, columnCount - 1] = 1

    for i in range(obstacleCount):  # rastgele engellerin yeri belirleniyor
        x, y = random.randrange(2, rowCount - 4), random.randrange(2, rowCount - 4)
        vertical = random.randrange(0, 2)
        for j in range(4):
            if vertical == 1:
                maze[x, y + j] = 1
            else:
                maze[x + j, y] = 1
    return maze


def startGame(sim,simno):  # simulasyonu başlatan fonksiyon
    sim.drawMaze()
    pygame.display.update()
    moveCount = 0
    generationCount = 0
    screenshot = str(simno) + "screenshot.jpg"

    play = True
    while play:  # bulunana kadar dönen döngü
        if sim.found == False:
            if moveCount < sim.dnaSize and sim.livingCount > 0:
                sim.move(moveCount)
                moveCount += 1
            else:
                sim.drawOnlyBest()
                generationCount += 1
                moveCount = 0
                sim.newPop(generationCount)
        else:
            # sim.resetAgents()
            print("simulation best agent move count:" + str(moveCount) + "generation:" + str(generationCount))
            moveCount = 0
            sim.changeMaze()
            pygame.image.save(sim.screen, screenshot)
            time.sleep(5)
            sim.reChangeMaze()
            play = False


if __name__ == "__main__":
    myFont = pygame.font.SysFont("Times New Roman", 18)
    test = myFont.render("Living Individuals:", 1, (255, 255, 255))
    test4 = myFont.render("Generation:", 1, (255, 255, 255))

    popsize1 = int(input("1.Simulasyon icin populasyon buyuklugunu girin: "))
    popsize2 = int(input("2.Simulasyon icin populasyon buyuklugunu girin: "))
    mutationRate1 = float(input("1.Simulasyon icin mutasyon oranini girin: "))
    mutationRate2 = float(input("2.Simulasyon icin mutasyon oranini girin: "))

    rowCount, columnCount, obstacleCount, dnasize = 20, 20, 10, 34

    maze = buildMaze(rowCount, columnCount, obstacleCount)

    sim = Simulation(rowCount, columnCount, obstacleCount, popsize1, mutationRate1, dnasize, maze, (190, 98, 0))
    start = timeit.default_timer()
    startGame(sim,1)

    sim2 = Simulation(rowCount, columnCount, obstacleCount, popsize2, mutationRate2, dnasize, maze, (11, 164, 228))
    start = timeit.default_timer()
    startGame(sim2,2)

