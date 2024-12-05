# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import math

# Constants for MovingObjectPosition
TYPE_NONE = -1
TYPE_BLOCK = 0
TYPE_ENTITY = 1

class Vector3(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def add(self, x, y, z):
        return Vector3(self.x + x, self.y + y, self.z + z)

    def subtract(self, x, y, z):
        return Vector3(self.x - x, self.y - y, self.z - z)

    def multiply(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def normalize(self):
        length = self.length()
        if length != 0:
            return Vector3(self.x / length, self.y / length, self.z / length)
        else:
            return Vector3(0, 0, 0)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def distanceSquared(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return dx*dx + dy*dy + dz*dz

    def distance(self, other):
        return math.sqrt(self.distanceSquared(other))

    def getIntermediateWithXValue(self, v, x):
        xDiff = v.x - self.x
        yDiff = v.y - self.y
        zDiff = v.z - self.z
        if xDiff * xDiff < 0.0000001:
            return None
        f = (x - self.x) / xDiff
        if f < 0 or f > 1:
            return None
        else:
            return Vector3(self.x + xDiff * f, self.y + yDiff * f, self.z + zDiff * f)

    def getIntermediateWithYValue(self, v, y):
        xDiff = v.x - self.x
        yDiff = v.y - self.y
        zDiff = v.z - self.z
        if yDiff * yDiff < 0.0000001:
            return None
        f = (y - self.y) / yDiff
        if f < 0 or f > 1:
            return None
        else:
            return Vector3(self.x + xDiff * f, self.y + yDiff * f, self.z + zDiff * f)

    def getIntermediateWithZValue(self, v, z):
        xDiff = v.x - self.x
        yDiff = v.y - self.y
        zDiff = v.z - self.z
        if zDiff * zDiff < 0.0000001:
            return None
        f = (z - self.z) / zDiff
        if f < 0 or f > 1:
            return None
        else:
            return Vector3(self.x + xDiff * f, self.y + yDiff * f, self.z + zDiff * f)

class AxisAlignedBB(object):
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ):
        self.minX = min(minX, maxX)
        self.minY = min(minY, maxY)
        self.minZ = min(minZ, maxZ)
        self.maxX = max(minX, maxX)
        self.maxY = max(minY, maxY)
        self.maxZ = max(minZ, maxZ)

    def isVectorInYZ(self, vector):
        return self.minY <= vector.y <= self.maxY and self.minZ <= vector.z <= self.maxZ

    def isVectorInXZ(self, vector):
        return self.minX <= vector.x <= self.maxX and self.minZ <= vector.z <= self.maxZ

    def isVectorInXY(self, vector):
        return self.minX <= vector.x <= self.maxX and self.minY <= vector.y <= self.maxY

    def calculateIntercept(self, pos1, pos2):
        v1 = pos1.getIntermediateWithXValue(pos2, self.minX)
        v2 = pos1.getIntermediateWithXValue(pos2, self.maxX)
        v3 = pos1.getIntermediateWithYValue(pos2, self.minY)
        v4 = pos1.getIntermediateWithYValue(pos2, self.maxY)
        v5 = pos1.getIntermediateWithZValue(pos2, self.minZ)
        v6 = pos1.getIntermediateWithZValue(pos2, self.maxZ)

        if v1 and not self.isVectorInYZ(v1):
            v1 = None
        if v2 and not self.isVectorInYZ(v2):
            v2 = None
        if v3 and not self.isVectorInXZ(v3):
            v3 = None
        if v4 and not self.isVectorInXZ(v4):
            v4 = None
        if v5 and not self.isVectorInXY(v5):
            v5 = None
        if v6 and not self.isVectorInXY(v6):
            v6 = None

        vector = None
        if v1:
            vector = v1
        if v2 and (not vector or pos1.distanceSquared(v2) < pos1.distanceSquared(vector)):
            vector = v2
        if v3 and (not vector or pos1.distanceSquared(v3) < pos1.distanceSquared(vector)):
            vector = v3
        if v4 and (not vector or pos1.distanceSquared(v4) < pos1.distanceSquared(vector)):
            vector = v4
        if v5 and (not vector or pos1.distanceSquared(v5) < pos1.distanceSquared(vector)):
            vector = v5
        if v6 and (not vector or pos1.distanceSquared(v6) < pos1.distanceSquared(vector)):
            vector = v6

        if vector is None:
            return None

        if vector == v1:
            sideHit = 4
        elif vector == v2:
            sideHit = 5
        elif vector == v3:
            sideHit = 0
        elif vector == v4:
            sideHit = 1
        elif vector == v5:
            sideHit = 2
        elif vector == v6:
            sideHit = 3
        else:
            sideHit = -1

        return MovingObjectPosition(TYPE_BLOCK, sideHit, vector)

class MovingObjectPosition(object):
    def __init__(self, typeOfHit, sideHit, hitVector, blockPos=None, block=None, entityHit=None):
        self.typeOfHit = typeOfHit  # type: int
        self.sideHit = sideHit  # type: int
        self.hitVector = hitVector  # type: Vector3
        self.blockPos = blockPos  # type: tuple[int, int, int]
        self.block = block  # type: tuple[str, int]
        self.entityHit = entityHit  # type: int

    @staticmethod
    def fromBlock(blockPos, sideHit, hitVector):
        return MovingObjectPosition(TYPE_BLOCK, sideHit, hitVector, blockPos=blockPos)

    @staticmethod
    def fromEntity(entityHit, hitVector):
        return MovingObjectPosition(TYPE_ENTITY, -1, hitVector, entityHit=entityHit)

class BlockClipIterator(object):
    def __init__(self, comp, startVec, endVec, liquid, ignoreBarrier, maxIteration):
        self.comp = comp  # BlockInfoComponentClient
        self.startVec = startVec
        self.endVec = endVec
        self.liquid = liquid
        self.ignoreBarrier = ignoreBarrier
        self.maxIteration = maxIteration

        self.currentVec = startVec.clone()
        self.currentIteration = 0
        self.blockStartX = int(math.floor(startVec.x))
        self.blockStartY = int(math.floor(startVec.y))
        self.blockStartZ = int(math.floor(startVec.z))
        self.blockEndX = int(math.floor(endVec.x))
        self.blockEndY = int(math.floor(endVec.y))
        self.blockEndZ = int(math.floor(endVec.z))
        self.blockCurrentX = self.blockStartX
        self.blockCurrentY = self.blockStartY
        self.blockCurrentZ = self.blockStartZ
        self.pointer = None
        self.finished = False

    def clip(self):
        while self.currentIteration < self.maxIteration:
            if (self.blockCurrentX == self.blockEndX and
                    self.blockCurrentY == self.blockEndY and
                    self.blockCurrentZ == self.blockEndZ):
                return None

            blockPos = (self.blockCurrentX, self.blockCurrentY, self.blockCurrentZ)
            blockName, blockAux = self.comp.GetBlock(blockPos)
            blockAABBData = self.comp.GetBlockCollision(blockPos)
            if blockAABBData:
                aabb = AxisAlignedBB(
                    blockAABBData['min'][0], blockAABBData['min'][1], blockAABBData['min'][2],
                    blockAABBData['max'][0], blockAABBData['max'][1], blockAABBData['max'][2]
                )
                hitResult = aabb.calculateIntercept(self.startVec, self.endVec)
                if hitResult:
                    hitResult.blockPos = blockPos
                    hitResult.block = (blockName, blockAux)
                    return hitResult

            self.step()
            self.currentIteration +=1
        return None

    def step(self):
        xClip = 0
        yClip = 0
        zClip = 0
        hasXClip = False
        hasYClip = False
        hasZClip = False

        if self.blockEndX > self.blockCurrentX:
            hasXClip = True
            xClip = self.blockCurrentX + 1
        elif self.blockEndX < self.blockCurrentX:
            hasXClip = True
            xClip = self.blockCurrentX
        if self.blockEndY > self.blockCurrentY:
            hasYClip = True
            yClip = self.blockCurrentY + 1
        elif self.blockEndY < self.blockCurrentY:
            hasYClip = True
            yClip = self.blockCurrentY
        if self.blockEndZ > self.blockCurrentZ:
            hasZClip = True
            zClip = self.blockCurrentZ + 1
        elif self.blockEndZ < self.blockCurrentZ:
            hasZClip = True
            zClip = self.blockCurrentZ

        xDist = float('inf')
        yDist = float('inf')
        zDist = float('inf')
        xd = self.endVec.x - self.currentVec.x
        yd = self.endVec.y - self.currentVec.y
        zd = self.endVec.z - self.currentVec.z

        if hasXClip and xd != 0:
            xDist = (xClip - self.currentVec.x) / xd
        if hasYClip and yd != 0:
            yDist = (yClip - self.currentVec.y) / yd
        if hasZClip and zd != 0:
            zDist = (zClip - self.currentVec.z) / zd

        if (yDist <= xDist) or (zDist <= xDist):
            if zDist <= yDist:
                if self.blockEndZ <= self.blockCurrentZ:
                    self.blockCurrentZ -=1
                else:
                    self.blockCurrentZ +=1
                self.currentVec.x += xd * zDist
                self.currentVec.y += yd * zDist
                self.currentVec.z = zClip
            else:
                if self.blockEndY <= self.blockCurrentY:
                    self.blockCurrentY -=1
                else:
                    self.blockCurrentY +=1
                self.currentVec.x += xd * yDist
                self.currentVec.y = yClip
                self.currentVec.z += zd * yDist
        else:
            if self.blockEndX <= self.blockCurrentX:
                self.blockCurrentX -=1
            else:
                self.blockCurrentX +=1
            self.currentVec.x = xClip
            self.currentVec.y += yd * xDist
            self.currentVec.z += zd * xDist

    def hasNext(self):
        if self.pointer:
            return True
        if self.finished:
            return False
        result = self.clip()
        if result is None:
            self.finished = True
            return False
        else:
            self.pointer = result
            return True

    def next(self):
        if not self.hasNext():
            raise StopIteration()
        result = self.pointer
        self.pointer = None
        return result

class RayHitTarget(object):
    def __init__(self, raycaster, target, distanceSq):
        self.raycaster = raycaster  # type: Raycaster
        self.target = target  # type: MovingObjectPosition
        self.distanceSq = distanceSq  # type: float

    def __lt__(self, other):
        return self.distanceSq < other.distanceSq

class Raycaster(object):
    def __init__(self, start, direction, maxDistance=120.0, maxBlockCollide=1, liquid=False, ignoreBarrier=False):
        self.start = start.clone()
        self.direction = direction.normalize()
        self.maxDistance = maxDistance
        self.liquid = liquid
        self.ignoreBarrier = ignoreBarrier
        self.maxBlockCollide = maxBlockCollide
        self.end = self.start.add(self.direction.x * maxDistance, self.direction.y * maxDistance, self.direction.z * maxDistance)

        # Get levelId (dimension ID)
        gameComp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())
        self.levelId = gameComp.GetCurrentDimension()

        self.blockComp = clientApi.GetEngineCompFactory().CreateBlockInfo(self.levelId)
        self.gameComp = clientApi.GetEngineCompFactory().CreateGame(self.levelId)

    def raytraceEntities(self, countLimit=1):
        localPlayerId = clientApi.GetLocalPlayerId()
        minX = min(self.start.x, self.end.x)
        minY = min(self.start.y, self.end.y)
        minZ = min(self.start.z, self.end.z)
        maxX = max(self.start.x, self.end.x)
        maxY = max(self.start.y, self.end.y)
        maxZ = max(self.start.z, self.end.z)
        startPos = (minX, minY, minZ)
        endPos = (maxX, maxY, maxZ)

        entities = self.gameComp.GetEntitiesInSquareArea(None, startPos, endPos)

        targets = []
        for entityId in entities:
            posComp = clientApi.GetEngineCompFactory().CreatePos(entityId)
            entityPos = Vector3(*posComp.GetPos())
            sizeComp = clientApi.GetEngineCompFactory().CreateCollisionBox(entityId)
            width, height = sizeComp.GetSize()

            minX = entityPos.x - width / 2
            minY = entityPos.y
            minZ = entityPos.z - width / 2
            maxX = entityPos.x + width / 2
            maxY = entityPos.y + height
            maxZ = entityPos.z + width / 2
            entityAABB = AxisAlignedBB(minX, minY, minZ, maxX, maxY, maxZ)

            hitResult = entityAABB.calculateIntercept(self.start, self.end)
            if hitResult:
                if entityId == localPlayerId:
                    continue
                hitResult.typeOfHit = TYPE_ENTITY
                hitResult.entityHit = entityId
                distanceSq = self.start.distanceSquared(hitResult.hitVector)
                targets.append(RayHitTarget(self, hitResult, distanceSq))
                if len(targets) >= countLimit:
                    break

        return targets

    def raytraceBlocks(self, countLimit=1):
        targets = []
        iterator = BlockClipIterator(self.blockComp, self.start, self.end, self.liquid, self.ignoreBarrier, int(self.maxDistance * 3))
        while iterator.hasNext() and len(targets) < self.maxBlockCollide:
            hitResult = iterator.next()
            distanceSq = self.start.distanceSquared(hitResult.hitVector)
            targets.append(RayHitTarget(self, hitResult, distanceSq))
            if len(targets) >= countLimit:
                break
        return targets

    def raytraceAll(self):
        """
        Raytrace all blocks and entities in the path of the ray
        :return: A list of RayHitTarget objects
        @rtype: list[RayHitTarget]
        """
        blockHits = self.raytraceBlocks()
        entityHits = self.raytraceEntities()
        allHits = blockHits + entityHits
        allHits.sort()
        return allHits
