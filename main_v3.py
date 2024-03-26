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

def within_distance(x_1, y_1, x_2, y_2, dis):
    if ((x_2 - x_1)**2  + (y_2 - y_1)**2)**(1/2) < dis:
        return True
    else:
        return False

    

def move_given_angle(x_1, y_1, angle, dis):

    new_x = math.cos(angle)*dis + x_1
    new_y = math.sin(angle)*dis + y_1
    #print(math.cos(angle)*dis)
    #print(f"this is the new x and new y :{new_x}, :{x_1}, the y:{new_y}, :{y_1}, ")

    return float(new_x), float(new_y)

def mutate(genes, rate, weights):
    #TODO
    new_genes = []
    for gene in genes:
        new_genes.append(gene*uniform(1-rate, 1+rate))
    
    weights = [weight + uniform(-rate, rate) for weight in weights]

    return new_genes , weights

def scaling_function(x):
    return math.e**(-0.01*x**2)

def length_vector(x, y):
    
    return ((x**2 + y**2)**(1/2))

def create_vectors(player_pos, creatue_positions):
    creature_vectors = [(creature.x - player_pos[0], creature.y - player_pos[1]) for creature in creatue_positions]
    return creature_vectors

def calculate_best_angle(player_pos, food_positions, blob_positions, predator_positions, food_magnitude, blob_magnitude, predator_magnitude):
    # Calculate vectors to food and predators
    food_vectors =  create_vectors(player_pos, food_positions)
    blob_vectors = create_vectors(player_pos, blob_positions)
    predator_vectors = create_vectors(player_pos, predator_positions)
    
    # Weight the vectors

    print(f"\nThis is all the vectors \n{food_vectors}, \n{blob_vectors}, \n {predator_vectors}\n")

    
    food_vectors = [( vec[0] * food_magnitude * scaling_function(length_vector(vec[0], vec[1])), vec[1] * food_magnitude * scaling_function(length_vector(vec[0], vec[1]))) for vec in food_vectors] 
    blob_vectors = [( vec[0] * blob_magnitude * scaling_function(length_vector(vec[0], vec[1])), vec[1] * blob_magnitude * scaling_function(length_vector(vec[0], vec[1]))) for vec in blob_vectors] 
    predator_vectors = [( vec[0] * predator_magnitude * scaling_function(length_vector(vec[0], vec[1])), vec[1] * predator_magnitude * scaling_function(length_vector(vec[0], vec[1]))) for vec in predator_vectors]
    
    # Combine vectors
    combined_vector = [0, 0]

    for vec_1, vec_2, vec_3 in zip(food_vectors, blob_vectors, predator_vectors):
        combined_vector = (combined_vector[0] + vec_1[0] + vec_2[0] + vec_3[0], combined_vector[1] + vec_1[1] + vec_2[1] + vec_3[1])

    print(combined_vector)
    # Calculate best angle
    angle = math.atan2(combined_vector[1], combined_vector[0])

    print(angle)
    return angle

def consumption(consumers, foods):
    for consumer in consumers:
        for food in foods:
            if consumer.rect.colliderect(food.rect):
                foods.pop(foods.index(food))
                consumer.erg += food.erg

    return foods

def action(creatures, creatures_stats, reproduction_cap, creature_type , all_creatures):
    # This function handles reproduction, dying, and moving the creatures
    # It returnes the creature list and the updated stats

    age = -1

    creatures_stats["oldest"] = None
    
    print("\n this is the beninging of the action\n")

    for creature in creatures:
        if creature.erg > 0:
            print("We livin dis shit")
            if creature.erg >= reproduction_cap:
                genes = [creature.speed, creature.vison]
                n_g, w_0 = mutate(genes, 0.1, creature.weights)
                b_0 = creature_type(creature.x, creature.y, n_g[0], n_g[1], w_0 )
                creatures.append(b_0)
                creature.erg -= 200

                creatures_stats["births"][-1] += 1

            if creature.timer <= 0:
                creature.move(all_creatures[0], all_creatures[1], all_creatures[2])
                creature.erg -= creature.erg_consumption
                creature.age += 1
            else:
                creature.timer -= 1

            if age != -1:
                if creature.age > age:
                    age = creature.age
                    creatures_stats["oldest"] = creature
                    print(f"We got a new old person: {creature}")
            else:
                age = creature.age
                print(f"We got a new old person: {creature}")
                creatures_stats["oldest"] = creature
            
        else :
            print(f"Dis ting do be dyin💀💀💀: {creature}")
            creatures_stats["deaths"][-1] += 1

            creatures.pop(creatures.index(creature)) 


    #Setting which creature is oldest
    if creatures_stats["oldest"] != None:
        o = creatures[creatures.index(creatures_stats["oldest"])]
        o.is_oldest = True

    return creatures, creatures_stats

def show_data(time, stats):

    a_v = stats["average_vison"]
    a_s = stats["average_speed"]
    population = stats["population"]
    deaths = stats["deaths"]
    births = stats["births"]


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
    def __init__(self,x, y, speed, vison, mags) :
        self.x = x 
        self.y = y
        self.size = 40
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.vison = vison
        self.angle = 5
        self.age = 0

        self.weights = mags
        self.food_magnitude = mags[0]
        self.blob_magnitude = mags[1]
        self.predator_magnitude = mags[2]


        self.is_oldest = False


        self.timer = 25 + randint(0, 400)

        if round(self.vison/5, 0) <= 254:
            self.s_v = round(self.vison/2, 0)
        else:
            self.s_v = 254

        if  self.speed * 5<= 255:
            self.s_p = self.speed *10
        else:
            self.s_p = 255

        self.color = (0,self.s_v,self.s_p )
        self.erg = 100
        self.erg_consumption = (self.speed**2 + 0.01*self.vison)*(1/100)

    def move(self,foods, blobs, predators ):
        #this is the function for calculating where the blob is going to move

        if self in blobs:
            blobs.pop(blobs.index(self))
        elif self in predators:
            predators.pop(predators.index(self))

        print(predators, blobs)

        foods_within_distance = [f for f in foods if within_distance(self.x, self.y, f.x, f.y, self.vison )]
        blobs_within_distance = [b for b in blobs if within_distance(self.x, self.y, b.x, b.y, self.vison )]
        predators_within_distance = [p for p in predators if within_distance(self.x, self.y, p.x, p.y, self.vison )]

        if foods_within_distance != None and blobs_within_distance!= None and predators_within_distance!= None:

            self.angle = calculate_best_angle((self.x, self.y), foods_within_distance, blobs_within_distance, predators_within_distance, self.food_magnitude, self.blob_magnitude, self.predator_magnitude)
        else:
            self.angle += uniform(-0.5, 0.5)


        """
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
        """
        

        self.x, self.y  = move_given_angle(self.x, self.y, self.angle, self.speed)

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        #print(f"Moved to {new_x}, {new_y}")

    
    def draw(self, WIN):
        pygame.draw.circle(WIN, self.color, (self.x, self.y), self.size)
        if self.is_oldest:
            pygame.draw.circle(WIN, (255, 94, 5), (self.x, self.y), self.size/5)


class predator(blob):
    def __init__(self,x, y, speed, vison, mags):
        super().__init__(x, y, speed, vison, mags)
        self.color = (250, self.s_v, self.s_p )



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
    #Defining variables to track the stats
    blob_stats = {  "average_vison" : [],
                    "average_speed" : [], 
                    "population" : [],
                    "deaths" : [],
                    "births" : [],
                    "oldest" : None
                  }
    
    predator_stats = {  "average_vison" : [],
                        "average_speed" : [], 
                        "population" : [],
                        "deaths" : [],
                        "births" : [],
                        "oldest" : None
                  }
    time = []


    blobs = []
    foods = []
    predators = []

    cords = [ [100,100] , [900,100], [100, 1700], [WIDTH/2, HEIGHT/2], [900, 1700] ]

    #Spawning in the creatures
    for c in cords: 
        b = blob(c[0], c[1], 20, 100, (0.1, 4, -0.1))
        blobs.append(b)

    for _ in range(3):
        b = blob(randint(1, WIDTH), randint(1, HEIGHT), 10, 200, (0.1, 4, -0.1))
        blobs.append(b)

    for _ in range(20):
        f = food(randint(1, WIDTH), randint(1, HEIGHT))
        foods.append(f)
    
    for _ in range(4):
        p = predator(randint(1, WIDTH), randint(1, HEIGHT), 10, 200, (4, 0.1, -4))
        predators.append(p)
    


    #counter variables 
    c = 1
    t = 0
    s = 0


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


        #Handles things eating each others           
        foods = consumption(blobs, foods)
        blobs = consumption(predators, blobs)



        #Handles reproduction and dying and such

        blobs, blob_stats = action(blobs, blob_stats, 600, blob, [foods, blobs, predators])
        predators, predator_stats = action(predators, predator_stats, 600, predator, [foods, blobs, predators])

        



        if c > 3:
            for i in range(1):
                f = food(randint(1, WIDTH), randint(1, HEIGHT))
                foods.append(f)  
            c = 0
        c += 1
        if s == 60:

            #Updating the statsn for blobs
            blob_stats["births"].append(0)
            blob_stats["deaths"].append(0)
            blob_stats["average_vison"].append(py.mean([b.vison for b in blobs]))
            blob_stats["average_speed"].append(py.mean([b.speed for b in blobs]))
            blob_stats["population"].append(len(blobs))
           
            #Updating the stats for predators
            predator_stats["births"].append(0)
            predator_stats["deaths"].append(0)
            predator_stats["average_vison"].append(py.mean([p.vison for p in predators]))
            predator_stats["average_speed"].append(py.mean([p.speed for p in predators]))
            predator_stats["population"].append(len(predators))
           

            time.append(t/60)
            s = 0


        draw_screen(WIN, foods, blobs)

        clock.tick(FPS)
        t += 1
        s += 1

    show_data(time, blob_stats)

    show_data(time, predator_stats)

    print("takk for meg")


if __name__ == "__main__":
    WIDTH , HEIGHT, WIN = init()
    main(WIN)