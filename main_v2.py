import pygame
from random import randint, uniform
import pylab as py
import math

from scipy.spatial.distance import cdist

def init():
    pygame.display.set_caption('Naturfag assa')
    pygame.display.init()
    (WIDTH, HEIGHT) = (1920, 1080)
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    return WIDTH, HEIGHT, WIN

def calculate_movement(x_1, x_2, y_1, y_2, s):
    #calculates where it can move to based on its reach labled s    

    delta_x = x_2 - x_1
    delta_y = y_2 - y_1

    u = (delta_x, delta_y)

    k = s/(u[0]**2 + u[1]**2)**(1/2)

    

    v = (k  * delta_x, k* delta_y)

    new_x = x_1 + v[0]

    new_y = y_1 + v[1]

    #print(f"This is the new x and y [{new_x},{new_y}] and this is the k:{k} \n this is the u : [{u[0]},{u[1]}], this is v : [{v[0]},{v[1]}]")

    return new_x, new_y

def move_given_angle(x_1, y_1, angle, dis):

    new_x = math.cos(angle)*dis + x_1
    new_y = math.sin(angle)*dis + y_1
    #print(math.cos(angle)*dis)
    #print(f"this is the new x and new y :{new_x}, :{x_1}, the y:{new_y}, :{y_1}, ")

    return float(new_x), float(new_y)

def mutate(genes, rate):
    new_genes = []
    for gene in genes:
        new_genes.append(gene*uniform(1-rate, 1+rate))
    return new_genes

def show_data(time, a_v, a_s, deaths, births, population):
    py.figure(1)
    py.plot(time, population, label="Populasjon over tid")
    py.legend()
    py.figure(2)
    py.plot(time, a_v, label="Gjennomsnittlig syn")
    py.legend()
    py.figure(3)
    py.plot(time, a_s, label = "Gjennomsnittlig hastighet")
    py.legend()
    py.figure(4)
    import statsmodels.api as sm

    lowess = sm.nonparametric.lowess

    z_1 = lowess(deaths, time, frac = 0.2, return_sorted = False) 

    py.plot(time, z_1, "g", label="Dødsfall lowess")
    py.legend()
    #py.plot(time, deaths, "b")

    py.figure(5)

    z_2 = lowess(births, time, frac = 0.2, return_sorted = False) 

    py.plot(time, z_2, "g", label="Fødseler lowess")
    #py.plot(time, births, "b")
    py.legend()
    py.show()



class blob():
    def __init__(self,x, y, speed, vison,) :
        self.x = x 
        self.y = y
        self.size = 40
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.vison = vison
        self.angle = 5
        self.age = 0

        self.is_oldest = False


        self.timer = 25 + randint(0, 400)

        if round(self.vison/5, 0) <= 254:
            s_v = round(self.vison/2, 0)
        else:
            s_v = 254
        if  self.speed * 5<= 255:
            s_p = self.speed *10
        else:
            s_p = 255
        self.color = (150,s_v,s_p )
        self.erg = 100
        self.erg_consumption = (self.speed**2 + 0.01*self.vison)*(1/100)

    def move(self,foods, blobs):
        #this is the function for calculating where the blob is going to move
        dis = None
        target = None

        for f in foods:
            d = cdist([[self.x, self.y]],[[f.x, f.y]], 'euclidean') 
            #print(f"This is the distance {d}, and this is the blobs x:{self.x}, and the foods x:{f.x} \n and this is the blobs y:{self.y}, and the foods y:{f.y}" )

            #blobs_cords = []
            #for blob in blobs:
                #blobs_cords.append([blob.x, blob.y])


            #b_d = cdist(blobs_cords, [[f.x, f.y]], "euclidean")[0]
            #print(f"this is the nearest blob distance{b_d}, and this the d {d}")
            if dis != None:
                if d < dis:
                    dis = d
                    target = f
                    #print(f"The new shortest distance is: {dis}")
            else:
                dis = d
                target = f
        f = target

        #print(self.x, self.y, "this is the foods coordinates", f.x, f.y)
        if not dis == None:
            if self.vison > dis:
                    
                if self.speed > dis:
                    new_x , new_y = f.x, f.y
                else:
                    new_x, new_y = calculate_movement(self.x, f.x, self.y, f.y ,self.speed)
                dis = ()

            else:
                self.angle += uniform(-0.5, 0.5)
                new_x, new_y = move_given_angle(self.x, self.y, self.angle, self.speed)
                #print(new_x, new_y, type(new_x), type(new_y))
                #new_x, new_y = self.x, self.y
        else:
            self.angle += uniform(-0.5, 0.5)
            new_x, new_y = move_given_angle(self.x, self.y, self.angle, self.speed)
            #new_x, new_y = self.x, self.y

        self.x, self.y  = new_x , new_y

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        #print(f"Moved to {new_x}, {new_y}")

    
    def draw(self, WIN):
        pygame.draw.circle(WIN, self.color, (self.x, self.y), self.size)
        if self.is_oldest:
            pygame.draw.circle(WIN, (255, 94, 5), (self.x, self.y), self.size/5)

class food():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.erg = 100
        self.size = 30
        self.rect = pygame.Rect(self.x-self.size/2, self.y-self.size/2, self.size, self.size)
    def draw(self,WIN):
        pygame.draw.circle(WIN,(50, 150, 10), (self.x, self.y), self.size)







def draw_screen(WIN,foods, blobs, bg_color=(255,255,255)):

    WIN.fill(bg_color)

    for f in foods:
        f.draw(WIN)
    for blob in blobs:
        blob.draw(WIN)
    
    pygame.display.update()



def main(WIN):

    average_speed = []
    average_vison =  []
    population = []
    deaths = []
    births = []
    time = []


    blobs = []
    foods = []

    cords = [ [100,100] , [900,100], [100, 1700], [WIDTH/2, HEIGHT/2], [900, 1700] ]

    for c in cords: 
        b = blob(c[0], c[1], 20, 100)
        blobs.append(b)

    for i in range(3):
        b = blob(randint(1, WIDTH), randint(1, HEIGHT), 10, 200)
        blobs.append(b)

    for i in range(20):
        f = food(randint(1, WIDTH), randint(1, HEIGHT))
        foods.append(f)
    c = 1
    t = 0
    s = 0
    death = 0
    birth = 0
    clock = pygame.time.Clock()
    FPS = 60
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                    
        for b in blobs:
            for f in foods:
                if b.rect.collidepoint((f.x, f.y)) == True:
                    foods.pop(foods.index(f))
                    b.erg += f.erg
        oldest = None
        age = None
        for b in blobs:
            if not b.erg <= 0:
                if b.erg >= 600:
                    genes = [b.speed, b.vison]
                    n_g = mutate(genes, 0.1)
                    b_0 = blob(b.x, b.y, n_g[0], n_g[1])
                    blobs.append(b_0)
                    birth += 1
                    b.erg -= 200
                if b.timer <= 0:
                    b.move(foods, blobs)
                    b.erg -= b.erg_consumption
                    b.age += 1
                else:
                    b.timer -= 1
                if age != None:
                    if b.age > age:
                        age = b.age
                        oldest = b
                else:
                    age = b.age
                    oldest = b
                
            else :
                death += 1

                blobs.pop(blobs.index(b))      
        o = blobs[blobs.index(oldest)]
        o.is_oldest = True



        if c > 3:
            for i in range(1):
                f = food(randint(1, WIDTH), randint(1, HEIGHT))
                foods.append(f)  
            c = 0
        c += 1
        if s == 60:
            births.append(birth)
            deaths.append(death)
            average_vison.append(py.mean([b.vison for b in blobs]))
            average_speed.append(py.mean([b.speed for b in blobs]))
            population.append(len(blobs))
            time.append(t/60)
            s = 0
            death = 0
            birth = 0

        draw_screen(WIN, foods, blobs)

        clock.tick(FPS)
        t += 1
        s += 1

    show_data(time, average_vison, average_speed, deaths, births, population)
    print("takk for meg")


if __name__ == "__main__":
    WIDTH , HEIGHT, WIN = init()
    main(WIN)