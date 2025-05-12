###### IMPORT ######
import mcschematic
import numpy as np
import random
from math import *
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL import Image
import copy
import os
import json

###### INITIALIZE ######
schem = mcschematic.MCSchematic()
scriptRoot = os.path.dirname(os.path.abspath(__file__))
print(f"You are running this program in the directory: {scriptRoot}")

###### OPERATOR FUNCTIONS ######
def clamp(value, range):
    return min(max(value, range[0]), range[1])

def dist(point1, point2):
    return sqrt((point2[1] - point1[1])**2 + (point2[0] - point1[0])**2)

def dist3D(point1, point2):
    return sqrt((point2[2] - point1[2])**2 + (point2[1] - point1[1])**2 + (point2[0] - point1[0])**2)

###### FUNCTIONS ######
def generateMountainMap(width, length, biomes=False):
    image = np.zeros((width, length), dtype=np.uint)
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            image[y][x] = random.randint(0,255)
    gen = Image.new("RGBA", (width, length))
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            gen.putpixel([y,x], (pixel, pixel, pixel))
    gen.save("images/mountains0.png")
    for iter in range(5):
        img = Image.open("images/mountains" + str(iter) + ".png")
        img = img.filter(ImageFilter.GaussianBlur((iter + 1)**1.4))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.9)
        #img = img.transpose(Image.ROTATE_90)
        img.save("images/mountains" + str(iter + 1) + ".png")
    
    opacities = [0.9, 0.8, 0.7, 0.5, 0.6]
    for iter in range(5):
        background = Image.blend(Image.open(f"images/mountains{iter}.png"), Image.open(f"images/mountains{iter + 1}.png"), opacities[iter])
        background.save(f"images/mountains{iter + 1}.png")

    if biomes:
        for iter in range(5,10):
            img = Image.open("images/mountains" + str(iter) + ".png")
            img = img.filter(ImageFilter.GaussianBlur((iter + 1)**1.5))
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
            #img = img.transpose(Image.ROTATE_90)
            img.save("images/mountains" + str(iter + 1) + ".png")
        opacities = [0.4, 0.4, 0.3, 0.3, 0.2]
        for iter in range(5,10):
            background = Image.blend(Image.open(f"images/mountains{iter}.png"), Image.open(f"images/mountains{iter + 1}.png"), opacities[iter - 5])
            background.save(f"images/mountains{iter + 1}.png")
    
    min = 99999
    max = 0
    bgArray = np.array(background.getdata()).reshape(background.size[1], background.size[0], 4)
    bgList = list(bgArray)
    for y, row in enumerate(bgList):
        for x, pixel in enumerate(row):
            if dist((x, y), (background.size[0] / 2, background.size[1] / 2)) < background.size[0] / 2:
                if pixel[0] > max:
                    max = pixel[0]
                if pixel[0] < min:
                    min = pixel[0]
    
    for row in bgList:
        for pixel in row:
            pixel = [(pixel[0] - min) * 255 / max, (pixel[0] - min) * 255 / max, (pixel[0] - min) * 255 / max, 255]

    pix = bgArray
    return pix

def generatePools(length, width, biomeMap, crackMap):
    global lavaAgents, waterAgents

    image = np.zeros((width, length), dtype=np.uint)

    lavaAgents = []
    waterAgents = []
    for initial in range(200):
        x, y = random.randint(0, length-1), random.randint(0, width-1)
        if biomeMap[y][x] == "desert" or biomeMap[y][x] == "plains":
            tooClose = False
            for agent in lavaAgents:
                if dist(agent, [x, y]) < 15:
                    tooClose = True
            for agent in waterAgents:
                if dist(agent, [x, y]) < 15:
                    tooClose = True
            if not tooClose:
                if biomeMap[y][x] == "plains":
                    if random.randint(0, 1) == 1:
                        lavaAgents.append([x, y])
                    else:
                        waterAgents.append([x, y])
                else:
                    lavaAgents.append([x, y])


    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            for agent in lavaAgents:
                if dist(agent, [x, y]) <= 3.5:
                    if (biomeMap[y][x] != "plains") or crackMap[y][x] != 255:
                        lavaAgents.remove(agent)
            for agent in waterAgents:
                if dist(agent, [x, y]) <= 3.5:
                    if (biomeMap[y][x] != "desert" and biomeMap[y][x] != "plains") or crackMap[y][x] != 255:
                        waterAgents.remove(agent)
    
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            for agent in lavaAgents:
                if dist(agent, [x, y]) <= 6:
                    image[x][y] = 1
            for agent in waterAgents:
                if dist(agent, [x, y]) <= 6:
                    image[x][y] = 2

    gen = Image.new("RGBA", (width, length))
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            if pixel == 1: #lava
                gen.putpixel([y, x], (255, 50, 10, 255))
            elif pixel == 2: #water
                gen.putpixel([y, x], (0, 0, 255, 255))
            else:
                gen.putpixel([y, x], (0, 0, 0, 255))
    
    gen.save("images/poolmap.png")
    return image


def generateCrackMap(width, length):
    image = np.zeros((width, length), dtype=np.uint)

    spacing = 20
    numVoronoiAgents = round((width / spacing) * (length / spacing))

    agents = []
    for iter in range(numVoronoiAgents):
        agents.append([random.randint(0, width - 1), random.randint(0, length - 1)])
    
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            coord = [x, y]
            distance = 99999
            for agent in agents:
                if dist(coord, agent) * 10 < distance:
                    oldDistance = distance
                    distance = dist(coord, agent) * 10
            if abs(clamp(oldDistance, (0, 255)) - clamp(distance, (0, 255))) > 30:
                if dist(coord, [width/2, length/2]) < min(width/2, length/2):
                    image[y][x] = 255
                else:
                    image[y][x] = 0
            else:
                image[y][x] = 0

    gen = Image.new("RGBA", (width, length))
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            gen.putpixel([y,x], (pixel, pixel, pixel))
    gen.save("images/map.png")
    return image

def generateBiomeMap(width, length):
    colors = [
        ["snow" , [245, 245, 255, 255]],
        ["plains" , [90, 170, 60, 255]],
        ["desert" , [220, 220, 160, 255]],
        ["shrooms" , [125, 105, 135, 255]]
    ]
    pix = generateMountainMap(width, length, biomes=True)
    gen = Image.new("RGBA", (width, length))
    biomeMap = []
    for y, row in enumerate(pix):
        rowBiomes = []
        for x, pixel in enumerate(row):
            if 180 <= list(pixel)[0] < 256:
                gen.putpixel([x, y], tuple(colors[3][1]))
                rowBiomes.append(colors[3][0])
            elif 145 <= list(pixel)[0] < 180:
                gen.putpixel([x, y], tuple(colors[2][1]))
                rowBiomes.append(colors[2][0])
            elif 90 <= list(pixel)[0] < 145:
                gen.putpixel([x, y], tuple(colors[1][1]))
                rowBiomes.append(colors[1][0])
            elif list(pixel)[0] < 90:
                gen.putpixel([x, y], tuple(colors[0][1]))
                rowBiomes.append(colors[0][0])
        biomeMap.append(rowBiomes)
    gen.save("images/biomes.png")
    return biomeMap

def generateIslandShape(length, width):
    global biomeMap
    spawnfile = json.load(open(f"{scriptRoot}"spawnfile.json""))
    ores = spawnfile['ORES']
    stoneVariants = spawnfile['STONE VARIANTS']
    shrubs = spawnfile['SHRUBS']

    def getBounds(item, string):
        L, U = item[string]['probability'] - item[string]['variance'], item[string]['probability'] + item[string]['variance']
        return L, U

    def voxelShader():
        global biomeMap, lavaAgents, waterAgents
        # the initial generations use the agent model to create structures that are spatially coherent, before they are applied in the probability model section.
        print("Spawning trees...")
        ### TREES ###
        treeCoords = []
        treeL, treeU = getBounds(shrubs, 'tree')
        for tree in range(random.randint(treeL,treeU)):
            newCoord = [random.randint(1, length), random.randint(1, width)]
            failed = False
            for coord in treeCoords:
                if dist(newCoord, coord) < 4:
                    failed = True
            if failed == False:
                treeCoords.append(newCoord)
        ### SHROOMS ###
        shroomCoords = []
        shroomL, shroomU = getBounds(shrubs, 'shroom')
        for shroom in range(random.randint(shroomL, shroomU)):
            newCoord = [random.randint(1, length), random.randint(1, width)]
            failed = False
            for coord in shroomCoords:
                if dist(newCoord, coord) < 10:
                    failed = True
            if failed == False:
                shroomCoords.append(newCoord)
        
        print("Spawning ores...")
        ### ORES ###
        # Andesite
        andesitePatchCoords = []
        andesiteL, andesiteU = getBounds(stoneVariants, 'andesite')
        for andesitePatch in range(random.randint(andesiteL, andesiteU)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in andesitePatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                andesitePatchCoords.append(newCoord)
        # Diorite
        dioritePatchCoords = []
        dioriteL, dioriteU = getBounds(stoneVariants, 'diorite')
        for dioritePatch in range(random.randint(dioriteL, dioriteU)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in dioritePatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                dioritePatchCoords.append(newCoord)
        # Granite
        granitePatchCoords = []
        graniteL, graniteU = getBounds(stoneVariants, 'granite')
        for granitePatch in range(random.randint(graniteL, graniteU)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in granitePatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                granitePatchCoords.append(newCoord)
        # Coal Ore
        coalPatchCoords = []
        coalL, coalU = getBounds(ores, 'coal')
        for coalPatch in range(random.randint(coalL, coalU)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in coalPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                coalPatchCoords.append(newCoord)
        # Copper Ore
        copperPatchCoords = []
        copperL, copperU = getBounds(ores, 'copper')
        for copperPatch in range(random.randint(copperL, copperU)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in copperPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                copperPatchCoords.append(newCoord)
        # Iron Ore
        ironPatchCoords = []
        ironL, ironU = getBounds(ores, 'iron')
        for ironPatch in range(random.randint(ironL, ironU)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in ironPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                ironPatchCoords.append(newCoord)
        # Lapis Ore
        lapisPatchCoords = []
        lapisL, lapisU = getBounds(ores, 'lapis')
        for lapisPatch in range(random.randint(lapisL, lapisU)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in lapisPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                lapisPatchCoords.append(newCoord)
        # Diamond Ore
        diamondPatchCoords = []
        diamondL, diamondU = getBounds(ores, 'diamond')
        for diamondPatch in range(random.randint(diamondL, diamondU)):
            newCoord = [random.randint(1, length), random.randint(-40, -20), random.randint(1, width)]
            failed = False
            for coord in diamondPatchCoords:
                if dist3D(newCoord, coord) < 20:
                    failed = True
            if failed == False:
                diamondPatchCoords.append(newCoord)

        print("Growing lava and water pools...")

        def spawnPool(type, coords):
            '''lets create a function to spawn a lava/water pool at a coordinate:'''
            poolBlocks = createDisc(coords, 2.5)
            borderBlocks = [block for block in createDisc(coords, 3.5) if not block in poolBlocks]
            for (x, y, z) in poolBlocks:
                schem.setBlock((x, y, z), ("lava" if type == 0 else "water"))
            for dY in range(0, 5):
                for (x, y, z) in borderBlocks:
                    if schem.getBlockDataAt((x, y + dY, z)) != "air" or dY == 0:
                        schem.setBlock((x, y + dY, z), ("lime_wool" if type == 0 else "green_wool"))
                for (x, y, z) in poolBlocks:
                    if schem.getBlockDataAt((x, y + dY, z)) != ("lava" if type == 0 else "water"):
                        schem.setBlock((x, y + dY, z), "air")

        def createDisc(coords, radius):
            '''first we create a disc from virtual block coordinates'''
            x, y, z = coords
            discBlocks = []
            for dX in range(-ceil(radius), ceil(radius)):
                for dZ in range(-ceil(radius), ceil(radius)):
                    if dist3D(coords, (x + dX, y, z + dZ)) < radius:
                        discBlocks.append((x + dX, y, z + dZ))
            
            return discBlocks
    
        def discIsInGround(discBlocks):
            '''we loop through all the blocks in a disc to see if *all* of them are in the ground.'''
            for (x, y, z) in discBlocks:
                if schem.getBlockDataAt((x, y, z)) == "air":
                    return False
            return True

        def dropPool(XZ):
            '''a function to generate a disc super high, and if it fails test we lower it by one until it fails or hits the bottom.'''
            x, z = XZ
            y = 1
            while y > -20:
                y -= 1
                if discIsInGround(createDisc((x, y, z), 2.5)):
                    return (x, y, z)
            return None
        
        def dropPools(lavaList, waterList):
            '''a master function to take the entire list of pools and perform the drop test on all of them'''
            for lavaPool in lavaList:
                output = dropPool(lavaPool)
                if output:
                    spawnPool(0, output)
            for waterPool in waterList:
                output = dropPool(waterPool)
                if output:
                    spawnPool(1, output)

        dropPools(lavaAgents, waterAgents)

        print("Growing grass, shrubs, and trees...")

        ys = []
        for z in range(width):
            for x in range(length):
                y = 150
                while y > -150 and (schem.getBlockDataAt((x, y, z)) == "minecraft:air" or schem.getBlockDataAt((x, y, z)) == "air" or schem.getBlockDataAt((x, y, z)) == "oak_leaves" or schem.getBlockDataAt((x, y, z)) == "spruce_leaves" or "brown_mushroom_block" in schem.getBlockDataAt((x, y, z)) or "red_mushroom_block" in schem.getBlockDataAt((x, y, z)) or "water" in schem.getBlockDataAt((x, y, z)) or "lava" in schem.getBlockDataAt((x, y, z)) or "lime_wool" in schem.getBlockDataAt((x, y, z)) or "green_wool" in schem.getBlockDataAt((x, y, z))):
                    if "green_wool" in schem.getBlockDataAt((x, y, z)):
                        sugarcaneSpawnChance = random.randint(0,3)
                        schem.setBlock((x, y, z), "dirt" if sugarcaneSpawnChance < 2 else "andesite")
                        if schem.getBlockDataAt((x, y + 1, z)) == "air" and schem.getBlockDataAt((x, y + 2, z)) == "air" and (schem.getBlockDataAt((x + 1, y, z)) == "water" or schem.getBlockDataAt((x - 1, y, z)) == "water" or schem.getBlockDataAt((x, y, z + 1)) == "water" or schem.getBlockDataAt((x, y, z - 1)) == "water"):
                            schem.setBlock((x, y + 1, z), "sugar_cane" if sugarcaneSpawnChance == 0 else "air")
                            schem.setBlock((x, y + 2, z), "sugar_cane" if sugarcaneSpawnChance == 0 else "air")
                    if "lime_wool" in schem.getBlockDataAt((x, y, z)):
                        schem.setBlock((x, y, z), "dirt" if random.randint(0,2) == 2 else "gravel")
                    y -= 1
                if schem.getBlockDataAt((x, y, z)) == "blue_wool":
                    ys.append(y)
                    ### SURFACE (GRASS, SAND, SNOW) ###
                    if biomeMap[z][x] == "plains":
                        schem.setBlock((x, y, z), "grass_block")
                    elif biomeMap[z][x] == "desert":
                        schem.setBlock((x, y, z), "sand")
                    elif biomeMap[z][x] == "snow":
                        schem.setBlock((x, y, z), "snow_block")
                    elif biomeMap[z][x] == "shrooms":
                        schem.setBlock((x, y, z), "mycelium")
                    ### SUBSURFACE (DIRT, SANDSTONE) ###
                    if biomeMap[z][x] == "plains" or biomeMap[z][x] == "shrooms":
                        for yDisplacement in range(3):
                            if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                                schem.setBlock((x, y - yDisplacement, z), "dirt")
                        if random.randint(1,2) == 1 and schem.getBlockDataAt((x, y - 3, z)) == "blue_wool":
                            schem.setBlock((x, y - 3, z), "dirt")
                    elif biomeMap[z][x] == "desert":
                        for yDisplacement in range(1):
                            if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                                schem.setBlock((x, y - yDisplacement, z), "sand")
                        schem.setBlock((x, y - 2, z), "sandstone")
                        for yDisplacement in range(1, 5):
                            if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                                schem.setBlock((x, y - yDisplacement, z), "sandstone")
                        if random.randint(1,2) == 1 and schem.getBlockDataAt((x, y - 5, z)) == "blue_wool":
                            schem.setBlock((x, y - 5, z), "sandstone")
                    elif biomeMap[z][x] == "snow":
                        for yDisplacement in range(2):
                            if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                                schem.setBlock((x, y - yDisplacement, z), "grass_block[snowy=true]")
                        for yDisplacement in range(2, 4):
                            if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                                schem.setBlock((x, y - yDisplacement, z), "dirt")
                        if random.randint(1,2) == 1 and schem.getBlockDataAt((x, y - 3, z)) == "blue_wool":
                            schem.setBlock((x, y - 3, z), "dirt")
                    ### STONE ###
                    for yDisplacement in range(3, 33):
                        if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                            schem.setBlock((x, y - yDisplacement, z), "stone")
                    ### GRASS AND SHRUBS ###
                    if biomeMap[z][x] == "plains" and poolMap[x][z] == 0:
                        if random.randint(1,200) == 1:
                            schem.setBlock((x, y + 1, z), "poppy")
                        if random.randint(1,300) == 1:
                            schem.setBlock((x, y + 1, z), "dandelion")
                        rand = random.randint(1,100)
                        if rand <= 17: # the value in the inequality is the % chance that there is grass above a grass block
                            schem.setBlock((x, y + 1, z), "grass")
                            if rand <= 2: # the value in the inequality is the % chance that there is tall grass above a grass block
                                schem.setBlock((x, y + 1, z), "tall_grass[half=lower]")
                                schem.setBlock((x, y + 2, z), "tall_grass[half=upper]")
                    if biomeMap[z][x] == "desert" and poolMap[x][z] == 0:
                        if random.randint(1,200) == 1:
                            schem.setBlock((x, y + 1, z), "dead_bush")
                        rand = random.randint(1,100)
                        if rand <= 1 and schem.getBlockDataAt((x + 1, y + 1, z)) == "air" and schem.getBlockDataAt((x - 1, y + 1, z)) == "air" and schem.getBlockDataAt((x, y + 1, z + 1)) == "air" and schem.getBlockDataAt((x, y + 1, z - 1)) == "air":
                            for yDisplacement in range(1, random.randint(3,5)):
                                schem.setBlock((x, y + yDisplacement, z), "cactus")
                    if biomeMap[z][x] == "shrooms":
                        if random.randint(1,100) == 1:
                            schem.setBlock((x, y + 1, z), "brown_mushroom")
                        if random.randint(1,150) == 1:
                            schem.setBlock((x, y + 1, z), "red_mushroom")

                    ### GROWTH (TREES, SHROOMS) ###
                    if [z, x] in treeCoords:
                        if biomeMap[z][x] == "plains" and poolMap[x][z] == 0:
                            treeHeight = random.randint(3,4)
                            for yDisplacement in range(treeHeight):
                                schem.setBlock((x, y + yDisplacement + 1, z), "oak_log")
                            for xDisplacement in range(-2, 3):
                                for zDisplacement in range(-2, 3):
                                    yDisplacement = treeHeight - 2
                                    if schem.getBlockDataAt((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement)) != "oak_log":
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement), "oak_leaves")
                                    yDisplacement = treeHeight - 1
                                    if ((xDisplacement in [-1, 0, 1] or zDisplacement in [-1, 0, 1]) or random.randint(1,2) == 2) and schem.getBlockDataAt((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement)) != "oak_log":
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement), "oak_leaves")
                                    yDisplacement = treeHeight
                                    if xDisplacement in [-1, 0, 1] and zDisplacement in [-1, 0, 1] and schem.getBlockDataAt((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement)) != "oak_log":
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement), "oak_leaves")
                                    yDisplacement = treeHeight + 1
                                    if ((xDisplacement == 0 and zDisplacement in [-1, 0, 1]) or (zDisplacement == 0 and xDisplacement in [-1, 0, 1])) and schem.getBlockDataAt((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement)) != "oak_log":
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z + zDisplacement), "oak_leaves")
                        if biomeMap[z][x] == "snow":
                            #print(f"Spruce tree at ({x}, {y}, {z}).")
                            widthMap = [
                                [1, 0, 1, 2, 1, 2, 3, 1],
                                [1, 0, 1, 2, 1, 2],
                                [0, 1, 0, 1, 2, 1, 2, 3],
                                [0, 1, 0, 1, 2, 1, 2, 1, 2]
                            ]
                            heightMap = [
                                9, 6, 9, 7
                            ]
                            leafHeightMap = [
                                10, 8, 10, 10
                            ]
                            tree = random.choice(widthMap)
                            logHeight = heightMap[widthMap.index(tree)]
                            leafHeight = leafHeightMap[widthMap.index(tree)]

                            yDisplacement = leafHeight
                            while yDisplacement > leafHeight - len(tree):
                                layerWidth = tree[leafHeight - yDisplacement]
                                for xDisplacement in range(-layerWidth, layerWidth + 1):
                                    for zDisplacement in range(-layerWidth, layerWidth + 1):
                                        if xDisplacement == 0 and zDisplacement == 0:
                                            if yDisplacement >= logHeight:
                                                schem.setBlock((x + xDisplacement, y + yDisplacement, z + zDisplacement), "spruce_leaves")
                                            else:
                                                schem.setBlock((x + xDisplacement, y + yDisplacement, z + zDisplacement), "spruce_log[axis=y]")
                                        else:
                                            if ceil(dist((xDisplacement, zDisplacement), (0, 0))) <= layerWidth:
                                                schem.setBlock((x + xDisplacement, y + yDisplacement, z + zDisplacement), "spruce_leaves")
                                yDisplacement -= 1
                            while yDisplacement > -1:
                                schem.setBlock((x, y + yDisplacement, z), "spruce_log[axis=y]")
                                yDisplacement -= 1
                    if [z, x] in shroomCoords:
                        if biomeMap[z][x] == "shrooms":
                            shroomType = random.randint(0,1)
                            shroomHeight = random.randint(5, 8)
                            for yDisplacement in range(shroomHeight):
                                schem.setBlock((x, y + yDisplacement + 1, z), "mushroom_stem")
                            if shroomType == 0:
                                for xDisplacement in range(-3, 4):
                                    for zDisplacement in range(-3, 4):
                                        if not (xDisplacement in [-3, 3] and zDisplacement in [-3, 3]):
                                            schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z +  zDisplacement), "brown_mushroom_block[down=false]")
                            elif shroomType == 1:
                                yDisplacement = shroomHeight
                                for xDisplacement in range(-1, 2):
                                    for zDisplacement in range(-1, 2):
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z +  zDisplacement), "red_mushroom_block[down=false]")
                                xDisplacement = 2
                                for yDisplacement in range(shroomHeight-3, shroomHeight):
                                    for zDisplacement in range(-1, 2):
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z +  zDisplacement), "red_mushroom_block[west=false,down=false]")
                                xDisplacement = -2
                                for yDisplacement in range(shroomHeight-3, shroomHeight):
                                    for zDisplacement in range(-1, 2):
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z +  zDisplacement), "red_mushroom_block[east=false,down=false]")
                                zDisplacement = 2
                                for yDisplacement in range(shroomHeight-3, shroomHeight):
                                    for xDisplacement in range(-1, 2):
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z +  zDisplacement), "red_mushroom_block[north=false,down=false]")
                                zDisplacement = -2
                                for yDisplacement in range(shroomHeight-3, shroomHeight):
                                    for xDisplacement in range(-1, 2):
                                        schem.setBlock((x + xDisplacement, y + yDisplacement + 1, z +  zDisplacement), "red_mushroom_block[south=false,down=false]")

        print("Growing ore patches...")
        for andesitePatch in andesitePatchCoords:
            size = random.randint(5, 7)
            for x in range(andesitePatch[0] - size, andesitePatch[0] + size):
                for y in range(andesitePatch[1] - size, andesitePatch[1] + size):
                    for z in range(andesitePatch[2] - size, andesitePatch[2] + size):
                        if dist3D([x, y, z], andesitePatch) < size and schem.getBlockDataAt((x, y, z)) == "stone":
                            schem.setBlock((x, y, z), "andesite")
        for dioritePatch in dioritePatchCoords:
            size = random.randint(4, 6)
            for x in range(dioritePatch[0] - size, dioritePatch[0] + size):
                for y in range(dioritePatch[1] - size, dioritePatch[1] + size):
                    for z in range(dioritePatch[2] - size, dioritePatch[2] + size):
                        if dist3D([x, y, z], dioritePatch) < size and (schem.getBlockDataAt((x, y, z)) == "stone" or schem.getBlockDataAt((x, y, z)) == "andesite"):
                            schem.setBlock((x, y, z), "diorite")
        for granitePatch in granitePatchCoords:
            size = random.randint(4, 6)
            for x in range(granitePatch[0] - size, granitePatch[0] + size):
                for y in range(granitePatch[1] - size, granitePatch[1] + size):
                    for z in range(granitePatch[2] - size, granitePatch[2] + size):
                        if dist3D([x, y, z], granitePatch) < size and (schem.getBlockDataAt((x, y, z)) == "stone" or schem.getBlockDataAt((x, y, z)) == "andesite" or schem.getBlockDataAt((x, y, z)) == "diorite"):
                            schem.setBlock((x, y, z), "granite")
        for coalPatch in coalPatchCoords:
            size = random.randint(2, 3)
            for x in range(coalPatch[0] - size, coalPatch[0] + size):
                for y in range(coalPatch[1] - size, coalPatch[1] + size):
                    for z in range(coalPatch[2] - size, coalPatch[2] + size):
                        if dist3D([x, y, z], coalPatch) < random.randint(1, size) and (schem.getBlockDataAt((x, y, z)) == "stone" or schem.getBlockDataAt((x, y, z)) == "andesite" or schem.getBlockDataAt((x, y, z)) == "diorite" or schem.getBlockDataAt((x, y, z)) == "granite"):
                            schem.setBlock((x, y, z), "coal_ore")
        for copperPatch in copperPatchCoords:
            size = 2
            for x in range(copperPatch[0] - size, copperPatch[0] + size):
                for y in range(copperPatch[1] - size, copperPatch[1] + size):
                    for z in range(copperPatch[2] - size, copperPatch[2] + size):
                        if dist3D([x, y, z], copperPatch) < random.randint(1, size) and (schem.getBlockDataAt((x, y, z)) == "stone" or schem.getBlockDataAt((x, y, z)) == "andesite" or schem.getBlockDataAt((x, y, z)) == "diorite" or schem.getBlockDataAt((x, y, z)) == "granite"):
                            schem.setBlock((x, y, z), "copper_ore")
        for ironPatch in ironPatchCoords:
            size = 2
            for x in range(ironPatch[0] - size, ironPatch[0] + size):
                for y in range(ironPatch[1] - size, ironPatch[1] + size):
                    for z in range(ironPatch[2] - size, ironPatch[2] + size):
                        if dist3D([x, y, z], ironPatch) < random.randint(1, size) and (schem.getBlockDataAt((x, y, z)) == "stone" or schem.getBlockDataAt((x, y, z)) == "andesite" or schem.getBlockDataAt((x, y, z)) == "diorite" or schem.getBlockDataAt((x, y, z)) == "granite"):
                            schem.setBlock((x, y, z), "iron_ore")
        for lapisPatch in lapisPatchCoords:
            size = 2
            for x in range(lapisPatch[0] - size, lapisPatch[0] + size):
                for y in range(lapisPatch[1] - size, lapisPatch[1] + size):
                    for z in range(lapisPatch[2] - size, lapisPatch[2] + size):
                        if dist3D([x, y, z], lapisPatch) < random.randint(1, size) and (schem.getBlockDataAt((x, y, z)) == "stone" or schem.getBlockDataAt((x, y, z)) == "andesite" or schem.getBlockDataAt((x, y, z)) == "diorite" or schem.getBlockDataAt((x, y, z)) == "granite"):
                            schem.setBlock((x, y, z), "lapis_ore")
        for diamondPatch in diamondPatchCoords:
            size = 2
            for x in range(diamondPatch[0] - size, diamondPatch[0] + size):
                for y in range(diamondPatch[1] - size, diamondPatch[1] + size):
                    for z in range(diamondPatch[2] - size, diamondPatch[2] + size):
                        if dist3D([x, y, z], diamondPatch) < random.randint(1, size) and (schem.getBlockDataAt((x, y, z)) == "stone" or schem.getBlockDataAt((x, y, z)) == "andesite" or schem.getBlockDataAt((x, y, z)) == "diorite" or schem.getBlockDataAt((x, y, z)) == "granite"):
                            schem.setBlock((x, y, z), "diamond_ore")
        
    print("Generating mountainous terrain...")
    mountains = generateMountainMap(length, width)
    print("Breaking up terrain into islands...")
    map = generateCrackMap(length, width)
    
    layer = copy.deepcopy(map)
    print("Generating biomes...")
    biomeMap = generateBiomeMap(length, width)

    print("Spawning lava and water pools...")
    poolMap = generatePools(length, width, biomeMap, map)

    print("Creating floating islands...")
    for depth in range(15):
        nextLayer = copy.deepcopy(layer)
        for y in range(length):
            for x in range(width):
                if x != 0 and x != width - 1 and y != 0 and y != length - 1:
                    if layer[y][x] == 255:
                        nextLayer[y][x] = 255
                    else:
                        nextLayer[y][x] = 0
                else:
                    nextLayer[y][x] = 0
        layer = nextLayer
        for z, row in enumerate(layer):
            for x, pixel in enumerate(row):
                if pixel == 255:
                    if depth > (mountains[x][z][0] / 15):
                        schem.setBlock((x, -depth, z), blockData="blue_wool")
                    else:
                        schem.setBlock((x, -depth, z), blockData="air")
                else:
                    schem.setBlock((x, -depth, z), blockData="air")
    for depth in range(15, 30):
        nextLayer = copy.deepcopy(layer)
        for y in range(length):
            for x in range(width):
                if x != 0 and x != width - 1 and y != 0 and y != length - 1:
                    if layer[y][x + 1] == 255 and layer[y][x - 1] == 255 and layer[y + 1][x] == 255 and layer[y - 1][x] == 255 or (((layer[y][x + 1] == 255 or layer[y][x - 1] == 255 or layer[y + 1][x] == 255 or layer[y - 1][x] == 255) and layer[y][x] == 255) and random.randint(0,10) < 6 and depth != 0):
                        nextLayer[y][x] = 255
                    else:
                        nextLayer[y][x] = 0
                else:
                    nextLayer[y][x] = 0
        layer = nextLayer

        for z, row in enumerate(layer):
            for x, pixel in enumerate(row):
                if pixel == 255:
                    if depth > (mountains[z][x][0] / 20 - 3):
                        schem.setBlock((x, -depth, z), blockData="blue_wool")
                    else:
                        schem.setBlock((x, -depth, z), blockData="air")
                else:
                    schem.setBlock((x, -depth, z), blockData="air")
    
    voxelShader()
    
    print("Performing final block corrections...")
    for x in range(length):
        for z in range(width):
            for y in range(-30, 10):
                """
                if "water" == schem.getBlockDataAt((x, y, z)):
                    #if ("air" in schem.getBlockDataAt((x + 1, y, z))) or ("air" in schem.getBlockDataAt((x - 1, y, z))) or ("air" in schem.getBlockDataAt((x, y, z + 1))) or ("air" in schem.getBlockDataAt((x, y, z - 1))):
                    schem.setBlock((x, y + 5, z), blockData='''command_block{"Command":"E: ''' + schem.getBlockDataAt((x + 1, y, z)).replace("minecraft:", "")[:10] + '''  W: ''' + schem.getBlockDataAt((x - 1, y, z)).replace("minecraft:", "")[:10] + '''  S: ''' + schem.getBlockDataAt((x, y, z + 1)).replace("minecraft:", "")[:10] + '''  N: ''' + schem.getBlockDataAt((x, y, z - 1)).replace("minecraft:", "")[:10] + '''"}''')
                    #schem.setBlock((x, y + 4, z), "red_wool")
                    #print('''command_block{"command":"''' + schem.getBlockDataAt((x + 1, y, z)).replace("minecraft:", "")[:10] + '''"}','{"text":"W: ''' + schem.getBlockDataAt((x - 1, y, z)).replace("minecraft:", "")[:10] + '''"}','{"text":"S: ''' + schem.getBlockDataAt((x, y, z + 1)).replace("minecraft:", "")[:10] + '''"}','{"text":"N: ''' + schem.getBlockDataAt((x, y, z - 1)).replace("minecraft:", "")[:10] + '''"}''')
                    #if "air" in schem.getBlockDataAt((x, y + 1, z)):   
                        #schem.setBlock((x, y + 5, z), "red_wool")
                        #schem.setBlock((x + 1, y, z), "red_wool")
                        #schem.setBlock((x - 1, y, z), "red_wool")
                        #schem.setBlock((x, y, z + 1), "red_wool")
                        #schem.setBlock((x, y, z - 1), "red_wool")
                if "lava" in schem.getBlockDataAt((x, y, z)):
                    #if "air" in schem.getBlockDataAt((x + 1, y, z)) or "air" in schem.getBlockDataAt((x - 1, y, z)) or "air" in schem.getBlockDataAt((x, y, z + 1)) or "air" in schem.getBlockDataAt((x, y, z - 1)):
                        schem.setBlock((x, y + 5, z), "red_wool")
                        #schem.setBlock((x + 1, y, z), "red_wool")
                        #schem.setBlock((x - 1, y, z), "red_wool")
                        #schem.setBlock((x, y, z + 1), "red_wool")
                        #schem.setBlock((x, y, z - 1), "red_wool")"""
                #if "lime_wool" in schem.getBlockDataAt((x, y, z)):
                        #schem.setBlock((x, y + 5, z), "red_wool")
    schem.save(os.path.abspath(os.getcwd()), "pvpisland", mcschematic.Version.JE_1_20_1)

def convertToJson(version):
    print("Converting schematic into json file...")
    schemData = []

    for x in range(0, 180):
        for z in range(0, 180):
            for y in range(-40, 50):
                blockData = schem.getBlockDataAt((x, y, z))
                if blockData != "minecraft:air" and blockData != "air":
                    block = {}
                    if not "minecraft:" in blockData:
                        block["_data"] = "minecraft:" + str(blockData)
                    else:
                        block["_data"] = str(blockData)
                    if (block["_data"] == "minecraft:grass") and version == "1.21":
                        block["_data"] = "minecraft:short_grass"
                    block["_x"] = x
                    block["_y"] = y
                    block["_z"] = z

                    schemData.append(block)

    json.dump(schemData, open("output.json", "w"))


###### MAIN ######
generateIslandShape(180, 180)
#convertToJson(version="1.21")