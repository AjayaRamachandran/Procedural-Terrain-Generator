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

###### OPERATOR FUNCTIONS ######
def clamp(value, range):
    return min(max(value, range[0]), range[1])

def dist(point1, point2):
    return sqrt((point2[1] - point1[1])**2 + (point2[0] - point1[0])**2)

def dist3D(point1, point2):
    return sqrt((point2[2] - point1[2])**2 + (point2[1] - point1[1])**2 + (point2[0] - point1[0])**2)

###### FUNCTIONS ######
def generateMountainMap(width, length):
    image = np.zeros((width, length), dtype=np.uint)
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            image[y][x] = random.randint(0,255)
    gen = Image.new("RGBA", (width, length))
    for y, row in enumerate(image):
        for x, pixel in enumerate(row):
            gen.putpixel([y,x], (pixel, pixel, pixel))
    gen.save("mountains0.png")
    for iter in range(5):
        img = Image.open("mountains" + str(iter) + ".png")
        img = img.filter(ImageFilter.GaussianBlur((iter + 1)**1.4))
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.9)
        #img = img.transpose(Image.ROTATE_90)
        img.save("mountains" + str(iter + 1) + ".png")
    
    background = Image.blend(Image.open("mountains0.png"), Image.open("mountains1.png"), 0.9)
    background.save("mountains1.png")
    background = Image.blend(Image.open("mountains1.png"), Image.open("mountains2.png"), 0.8)
    background.save("mountains2.png")
    background = Image.blend(Image.open("mountains2.png"), Image.open("mountains3.png"), 0.7)
    background.save("mountains3.png")
    background = Image.blend(Image.open("mountains3.png"), Image.open("mountains4.png"), 0.5)
    background.save("mountains4.png")
    background = Image.blend(Image.open("mountains4.png"), Image.open("mountains5.png"), 0.6)
    background.save("mountains5.png")
    pix = np.array(background.getdata()).reshape(background.size[0], background.size[1], 4)
    return pix

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
    gen.save("map.png")
    return image
        

def generateIslandShape(length, width):
    def voxelShader():
        # the initial generations use the agent model to create structures that are spatially coherent, before they are applied in the probability model section.
        print("Initializing agents...")
        ### TREES ###
        treeCoords = []
        for tree in range(random.randint(100,150)):
            newCoord = [random.randint(1, length), random.randint(1, width)]
            failed = False
            for coord in treeCoords:
                if dist(newCoord, coord) < 4:
                    failed = True
            if failed == False:
                treeCoords.append(newCoord)
        ### ORES ###
        # Andesite
        andesitePatchCoords = []
        for andesitePatch in range(random.randint(600, 800)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in andesitePatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                andesitePatchCoords.append(newCoord)
        # Diorite
        dioritePatchCoords = []
        for dioritePatch in range(random.randint(100, 130)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in dioritePatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                dioritePatchCoords.append(newCoord)
        # Granite
        granitePatchCoords = []
        for granitePatch in range(random.randint(70, 100)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in granitePatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                granitePatchCoords.append(newCoord)
        # Coal Ore
        coalPatchCoords = []
        for coalPatch in range(random.randint(3000, 3400)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in coalPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                coalPatchCoords.append(newCoord)
        # Copper Ore
        copperPatchCoords = []
        for copperPatch in range(random.randint(2200, 2400)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in copperPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                copperPatchCoords.append(newCoord)
        # Iron Ore
        ironPatchCoords = []
        for ironPatch in range(random.randint(1800, 2000)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in ironPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                ironPatchCoords.append(newCoord)
        # Lapis Ore
        lapisPatchCoords = []
        for lapisPatch in range(random.randint(600, 750)):
            newCoord = [random.randint(1, length), random.randint(-40, 0), random.randint(1, width)]
            failed = False
            for coord in lapisPatchCoords:
                if dist3D(newCoord, coord) < 12:
                    failed = True
            if failed == False:
                lapisPatchCoords.append(newCoord)
        # Diamond Ore
        diamondPatchCoords = []
        for diamondPatch in range(random.randint(250, 300)):
            newCoord = [random.randint(1, length), random.randint(-40, -20), random.randint(1, width)]
            failed = False
            for coord in diamondPatchCoords:
                if dist3D(newCoord, coord) < 20:
                    failed = True
            if failed == False:
                diamondPatchCoords.append(newCoord)

        print("Running probability-based voxel shader...")
        ys = []
        for x in range(length):
            for z in range(width):
                y = 150
                while y > -150 and (schem.getBlockDataAt((x, y, z)) == "minecraft:air" or schem.getBlockDataAt((x, y, z)) == "air" or schem.getBlockDataAt((x, y, z)) == "oak_leaves"):
                    y -= 1
                if schem.getBlockDataAt((x, y, z)) == "blue_wool":
                    ys.append(y)
                    ### GRASS BLOCK ###
                    schem.setBlock((x, y, z), "grass_block")
                    ### DIRT ###
                    for yDisplacement in range(3):
                        if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                            schem.setBlock((x, y - yDisplacement, z), "dirt")
                    if random.randint(1,2) == 1 and schem.getBlockDataAt((x, y - 3, z)) == "blue_wool":
                        schem.setBlock((x, y - 3, z), "dirt")
                    ### STONE ###
                    for yDisplacement in range(3, 33):
                        if schem.getBlockDataAt((x, y - yDisplacement, z)) == "blue_wool":
                            schem.setBlock((x, y - yDisplacement, z), "stone")
                    ### GRASS AND SHRUBS ###
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
                    if [x, z] in treeCoords:
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
                #while y > -150:
                    #y -= 1
        print("Running agent-based voxel shader...")
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
        #print(ys)
    print("Generating mountainous terrain...")
    mountains = generateMountainMap(length, width)
    print("Dividing terrain into islands...")
    map = generateCrackMap(length, width)
    print("Converting data into schematic...")
    layer = copy.deepcopy(map)
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
                    if depth > (mountains[z][x][0] / 15):
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
    schem.save(os.path.abspath(os.getcwd()), "pvpisland", mcschematic.Version.JE_1_20_1)

generateIslandShape(180, 180)
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
                block["_x"] = str(x)
                block["_y"] = str(y)
                block["_z"] = str(z)

                schemData.append(block)

output = json.dump(schemData, open("output.json", "w"))