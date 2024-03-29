import pygame
from random import randint, uniform
import pylab as py
import math
import pygame.gfxdraw
import statsmodels.api as sm
#from scipy.spatial.distance import cdist

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
    
    weights = [weight *uniform(1-rate, 1+rate) for weight in weights]

    return new_genes , weights

def scaling_function(x):
    return 1/ (x + 0.0001)

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
    
 
    if food_vectors == []:
        food_vectors = [[0,0]]

    if blob_vectors == []:
        blob_vectors = [[0,0]]

    if predator_vectors == []:
        predator_vectors = [[0,0]]
    #print(f"\nThis is all the vectors \n{food_vectors}, \n{blob_vectors}, \n {predator_vectors}\n")


    food_lengths = [length_vector(*vector) for vector in food_vectors]
    blob_lengths = [length_vector(*vector) for vector in blob_vectors]
    predator_lengths = [length_vector(*vector) for vector in predator_vectors]

    food_vectors = [( vec[0] / (length + 0.001) * food_magnitude * scaling_function(length), vec[1] / ( length + 0.001) * food_magnitude * scaling_function(length)) for vec, length in zip(food_vectors, food_lengths)] 
    blob_vectors = [( vec[0] / (length + 0.001) * blob_magnitude * scaling_function(length), vec[1] / (length + 0.001) * blob_magnitude * scaling_function(length)) for vec, length in zip(blob_vectors, blob_lengths)] 
    predator_vectors = [( vec[0] / (length + 0.001) * predator_magnitude * scaling_function(length), vec[1] / (length + 0.001) * predator_magnitude * scaling_function(length)) for vec , length in zip(predator_vectors, predator_lengths)]
    
    #print(food_vectors)

    """
    food_vectors = [( vec[0] * food_magnitude * scaling_function(length_vector(vec[0], vec[1])), vec[1] * food_magnitude * scaling_function(length_vector(vec[0], vec[1]))) for vec in food_vectors] 
    blob_vectors = [( vec[0] * blob_magnitude * scaling_function(length_vector(vec[0], vec[1])), vec[1] * blob_magnitude * scaling_function(length_vector(vec[0], vec[1]))) for vec in blob_vectors] 
    predator_vectors = [( vec[0] * predator_magnitude * scaling_function(length_vector(vec[0], vec[1])), vec[1] * predator_magnitude * scaling_function(length_vector(vec[0], vec[1]))) for vec in predator_vectors]
    """

    # Combine vectors
    combined_vector = [0, 0]

    for vec_1, vec_2, vec_3 in zip(food_vectors, blob_vectors, predator_vectors):
        combined_vector = [combined_vector[0] + vec_1[0] + vec_2[0] + vec_3[0], combined_vector[1] + vec_1[1] + vec_2[1] + vec_3[1]]


    null_vector = False

    if combined_vector == [0.0, 0.0]:
        #print(f"The vector is null vector{combined_vector}")
        null_vector = True
        #print(f"The vector is not (shocker) null vector{combined_vector}")

    #i = input()
    #print(f"This is the combined vector{combined_vector}") 
    # Calculate best angle
    angle = math.atan2(combined_vector[1], combined_vector[0])

    #print(angle)
    return angle , null_vector, combined_vector

def consumption(consumers, foods, is_predator = False, food_stats = {}):

    for consumer in consumers:
        for food in foods:
            if consumer.rect.colliderect(food.rect):
                foods.pop(foods.index(food))
                if is_predator:
                    food_stats["deaths"][-1] += 1
                consumer.erg += food.erg

    return foods, food_stats

def action(creatures, creatures_stats, reproduction_cap, creature_type , all_creatures):
    # This function handles reproduction, dying, and moving the creatures
    # It returnes the creature list and the updated stats
    age = -1

    creatures_stats["oldest"] = None
    
    
    #print("\n this is the beninging of the action\n")

    for creature in creatures:
        if creature.erg > 0:
            #print("We livin dis shit")
            if creature.erg >= reproduction_cap:
                genes = [creature.speed, creature.vison]
                n_g, w_0 = mutate(genes, 0.1, creature.weights)
                b_0 = creature_type(creature.x, creature.y, n_g[0], n_g[1], w_0 )
                creatures.append(b_0)
                creature.erg -= 200
                

                creatures_stats["births"][-1] += 1


            
            creature.move(all_creatures[0], all_creatures[1], all_creatures[2])
            creature.erg -= creature.erg_consumption
            creature.age += 1

            if age != -1:
                if creature.age > age:
                    age = creature.age
                    creatures_stats["oldest"] = creature
                    #print(f"We got a new old person: {creature}")
            else:
                age = creature.age
                #print(f"We got a new old person: {creature}")
                creatures_stats["oldest"] = creature
            
        else :
            #print(f"Dis ting do be dyin💀💀💀: {creature}")
                 
            creatures_stats["deaths"][-1] += 1



            creatures.pop(creatures.index(creature)) 


    #Setting which creature is oldest
    if creatures_stats["oldest"] != None:
        o = creatures[creatures.index(creatures_stats["oldest"])]
        o.is_oldest = True

    return creatures, creatures_stats

def show_data(time, stats_1, stats_2):

    #a_v = stats["average_vison"]
    #a_s = stats["average_speed"]
    #population = stats["population"]
    #deaths = stats_1["deaths"]
    #births = stats_1["births"]


    py.figure(1)
    py.plot(time, stats_1["population"], color = "b", label="Blobbers populasjon over tid")
    py.plot(time, stats_2["population"], color = "r", label="Rovdyrs populasjon over tid")
    py.legend()
    py.figure(2)
    py.plot(time, stats_1["average_vison"], color = "b", label="Gjennomsnittlig syn")
    py.plot(time, stats_2["average_vison"], color = "r", label="Gjennomsnittlig syn")
    py.legend()
    py.figure(3)
    py.plot(time, stats_1["average_speed"], color = "b", label = "Gjennomsnittlig hastighet")
    py.plot(time, stats_2["average_speed"], color = "r", label = "Gjennomsnittlig hastighet")
    py.legend()
    py.figure(4)
    

    lowess = sm.nonparametric.lowess


    z_1 = lowess(stats_1["deaths"], time, frac = 0.2, return_sorted = False) 
    z_2 = lowess(stats_2["deaths"], time, frac = 0.2, return_sorted = False) 
    py.plot(time, z_1, "b", label="Dødsfall lowess")
    py.plot(time, z_2, "r", label="Dødsfall lowess")
    py.legend()
    #py.plot(time, deaths, "b")

    py.figure(5)

    
    z_3 = lowess(stats_1["births"], time, frac = 0.2, return_sorted = False) 
    z_4 = lowess(stats_2["births"], time, frac = 0.2, return_sorted = False) 
    py.plot(time, z_3, "b", label="Fødseler lowess")
    py.plot(time, z_4, "r", label="Fødseler lowess")
    #py.plot(time, births, "b")
    py.legend()
    py.show()


class blob():
    def __init__(self,x, y, speed, vison, mags) :
        self.x = x 
        self.y = y
        self.size = 10
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.vison = vison
        self.angle = 5
        self.age = 0
        self.predator = False
        self.see_vison = False
        self.weights = mags
        self.food_magnitude = mags[0]
        self.blob_magnitude = mags[1]
        self.predator_magnitude = mags[2]
        self.vector = []


        self.is_oldest = False


        self.timer = 25 + randint(0, 400)

        if round(self.vison/5, 0) <= 254:
            self.s_v = round(self.vison/2, 0)
        else:
            self.s_v = 254

        if  self.speed * 5<= 255:
            self.s_p = round(self.speed *10, 0)
        else:
            self.s_p = 255

        self.color = (0 , self.s_v , self.s_p )
        self.erg = 100
        self.erg_consumption = (self.speed**2 + 0.05*self.vison)*(1/50) 

    def move(self,foodss, blobss, predatorss ):
        #this is the function for calculating where the blob is going to move


        #copying the lists to later pop element so that it doesn't affect the whole list globalys
        foods = foodss[:]
        blobs = blobss[:]
        predators = predatorss[:]
        self.vector = []

        if self in blobs:
            blobs.pop(blobs.index(self))
        elif self in predators:
            predators.pop(predators.index(self))

        #print(f"\n This is the predators with the self removec {predators} \n And this is the blobs with the self removed {blobs}\n")
        
        
        """
        if self in blobs:
            print("sjet")
        elif self in predators:
            print("søren")
        else:
            print("jeppers")
        """


        foods_within_distance = [f for f in foods if within_distance(self.x, self.y, f.x, f.y, self.vison )]
        blobs_within_distance = [b for b in blobs if within_distance(self.x, self.y, b.x, b.y, self.vison )]
        predators_within_distance = [p for p in predators if within_distance(self.x, self.y, p.x, p.y, self.vison )]

        """
        if self in blobs_within_distance:
            print("Nemmen")
        elif self in predators_within_distance:
            print("dævens")
        """

        if foods_within_distance != [] or blobs_within_distance!= [] or predators_within_distance!= []:

            angle, null_vector_check, self.vector = calculate_best_angle((self.x, self.y), foods_within_distance, blobs_within_distance, predators_within_distance, self.food_magnitude, self.blob_magnitude, self.predator_magnitude)
            
            if null_vector_check == True:
                self.angle += uniform(-0.5, 0.5)  
            else:
                self.angle = angle
                #print(null_vector_check)

        else:
            #print("There is nothing within the sense")
            self.angle += uniform(-0.5, 0.5)

        self.x, self.y  = move_given_angle(self.x, self.y, self.angle, self.speed)

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        #print(f"Moved to {new_x}, {new_y}")

    
    def draw(self, WIN):

        if self.see_vison == True:
            pygame.gfxdraw.filled_circle(WIN, int(round(self.x, 0)), int(round(self.y, 0)), int(round(self.vison, 0)), (*self.color, 100))

        pygame.draw.circle(WIN, self.color, (self.x, self.y), self.size)
        if self.is_oldest:
            pygame.draw.circle(WIN, (255, 94, 5), (self.x, self.y), self.size/5)

        if self.predator == True:
            pygame.draw.circle(WIN, (255, 0, 0), (self.x, self.y), self.size/5)
        #if self.vector != [] and self.vector != [0.0,0.0]:
            #print(self.vector)
            #pygame.draw.line(WIN, (155, 155, 0), (self.x, self.y), (self.x + self.vector[0]*10**4, self.y + self.vector[1]*10**4), 10)


class predator(blob):
    def __init__(self,x, y, speed, vison, mags):
        super().__init__(x, y, speed, vison, mags)
        self.color = (250,0,0 )
        self.predator = True



class food():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.erg = 600
        self.size = 7.5
        self.rect = pygame.Rect(self.x-self.size/2, self.y-self.size/2, self.size, self.size)
    def draw(self,WIN):
        pygame.draw.circle(WIN,(50, 150, 10), (self.x, self.y), self.size)







def draw_screen(WIN,foods, blobs, predators, bg_color=(255,255,255)):

    WIN.fill(bg_color)

    for f in foods:
        f.draw(WIN)
    for blob in blobs:
        blob.draw(WIN)
    for predator in predators:
        predator.draw(WIN)
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
    

    foods = []
    blobs = []
    predators = []

    cords = [ [100,100] , [900,100], [100, 1700], [WIDTH/2, HEIGHT/2], [900, 1700] ]

    #Spawning in the creatures
    """
    for c in cords: 
        b = blob(c[0], c[1], 20, 100, (4, 0.1, -0.5))
        blobs.append(b)
    """
    
    for _ in range(60):
        b = blob(randint(1, WIDTH), randint(1, HEIGHT), 4, 100, (1, -0.1, -1))
        blobs.append(b)
    
    for _ in range(250):
        f = food(randint(1, WIDTH), randint(1, HEIGHT))
        foods.append(f)
    
    for _ in range(10):
        p = predator(randint(1, WIDTH), randint(1, HEIGHT), 5, 75, (0, 1, -0.1))
        predators.append(p)


    #counter variables 
    c = 1
    t = 0
    s = 0

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

    time = [0]
    
    clock = pygame.time.Clock()
    FPS = 120

    display_screen = 1
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                if event.key == pygame.K_f:
                    f = food(randint(1, WIDTH), randint(1, HEIGHT))
                    foods.append(f)
                if event.key == pygame.K_b:
                    b = blob(randint(1, WIDTH), randint(1, HEIGHT), 2, 100, (1, 0, -2))
                    blobs.append(b)
                if event.key == pygame.K_p:
                    p = predator(randint(1, WIDTH), randint(1, HEIGHT), 2.5, 75, (0, 1, 0))
                    predators.append(p)
                if event.key == pygame.K_s:
                    display_screen *= -1

        #updating these stats first to prevent bugs
        

        


        #Handles things eating each others           
        foods, trash = consumption(blobs, foods)
        blobs, blob_stats = consumption(predators, blobs, is_predator = True, food_stats = blob_stats)



        #Handles reproduction and dying and such

        blobs, blob_stats = action(blobs, blob_stats, 600, blob, [foods, blobs, predators])

        predators, predator_stats = action(predators, predator_stats, 600, predator, [foods, blobs, predators])

        



        if c > 2:
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

        if display_screen == 1:
            draw_screen(WIN, foods, blobs, predators)



        clock.tick(FPS)
        t += 1
        s += 1

    show_data(time, blob_stats, predator_stats)

    #show_data(time, predator_stats)

    print("takk for meg")


if __name__ == "__main__":
    WIDTH , HEIGHT, WIN = init()
    main(WIN)