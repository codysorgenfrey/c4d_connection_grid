# Copyright (C) 2019 Cody Sorgenfrey
import c4d
import os

class res(object):
    CONNECTION_GRID_NETWORK_CONNECTION_GROUP = 1000
    CONNECTION_GRID_NETWORK_CONNECTION_GRID_UNIT_LENGTH = 1001
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER = 1002
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER_XYZ = 1
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER_XZY = 2
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER_YXZ = 3
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER_YZX = 4
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER_ZYX = 5
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER_ZXY = 6
res = res()


def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp



def snap(v, mult, validate):
    vals = [int(round(v.x / mult)) * mult, int(round(v.y / mult)) * mult, int(round(v.z / mult)) * mult]
    if validate:
        for i in vals:
            if i == 0:
                i = mult

    return c4d.Vector(vals[0], vals[1], vals[2])



def compX(endSpacer, points):
    lastIn = points.pop()
    if lastIn.x != endSpacer.x:
        points.append(lastIn)
        lastIn = c4d.Vector(endSpacer.x, lastIn.y, lastIn.z)
        points.append(lastIn)

def compY(endSpacer, points):
    lastIn = points.pop()
    if lastIn.y != endSpacer.y:
        points.append(lastIn)
        lastIn = c4d.Vector(lastIn.x, endSpacer.y, lastIn.z)
        points.append(lastIn)

def compZ(endSpacer, points):
    lastIn = points.pop()
    if lastIn.z != endSpacer.z:
        points.append(lastIn)
        lastIn = c4d.Vector(lastIn.x, lastIn.y, endSpacer.z)
        points.append(lastIn)

class connectiongridData(c4d.plugins.ObjectData):
    PLUGIN_ID = 1053026
    PLUGIN_NAME = 'connection grid'
    PLUGIN_INFO = c4d.OBJECT_GENERATOR | c4d.OBJECT_ISSPLINE | c4d.OBJECT_INPUT
    PLUGIN_DESC = 'Oconnectiongrid'
    PLUGIN_ICON = load_bitmap('res/icons/connection grid.tiff')
    PLUGIN_DISKLEVEL = 0
    LAST_FRAME = 0
    INPUT_SPLINE = None
    UPDATE = True

    @classmethod
    def Register(cls):
        return c4d.plugins.RegisterObjectPlugin(
            cls.PLUGIN_ID,
            cls.PLUGIN_NAME,
            cls,
            cls.PLUGIN_DESC,
            cls.PLUGIN_INFO,
            cls.PLUGIN_ICON,
            cls.PLUGIN_DISKLEVEL
        )

    def Init(self, node):
        self.InitAttr(node, float, [res.CONNECTION_GRID_NETWORK_CONNECTION_GRID_UNIT_LENGTH])
        self.InitAttr(node, int, [res.CONNECTION_GRID_NETWORK_CONNECTION_ORDER])

        node[res.CONNECTION_GRID_NETWORK_CONNECTION_GRID_UNIT_LENGTH] = 10.0
        node[res.CONNECTION_GRID_NETWORK_CONNECTION_ORDER] = 1

        doc = c4d.documents.GetActiveDocument()
        self.LAST_FRAME = doc.GetTime().GetFrame(doc.GetFps())

        return True

    def CheckDirty(self, op, doc) :
        frame = doc.GetTime().GetFrame(doc.GetFps())
        if frame != self.LAST_FRAME:
            self.LAST_FRAME = frame
            op.SetDirty(c4d.DIRTYFLAGS_DATA)
        
        if self.UPDATE:
            self.UPDATE = False
            op.SetDirty(c4d.DIRTYFLAGS_DATA)

    def MakeSpline(self, gridUnit, order):
        inPoints = self.INPUT_SPLINE.GetAllPoints()
        outPoints = []

        for x in range(len(inPoints) - 1):
            p1 = inPoints[x]
            p2 = inPoints[x + 1]

            outPoints.append(p1)

            startSpacer = snap(p1 + c4d.Vector(gridUnit, 0, 0), gridUnit, False)
            outPoints.append(startSpacer)

            endSpacer = snap(p2 + c4d.Vector(gridUnit, 0, 0), gridUnit, False)

            if order == 2:
                compX(endSpacer, outPoints)
                compZ(endSpacer, outPoints)
                compY(endSpacer, outPoints)
            elif order == 3:
                compY(endSpacer, outPoints)
                compX(endSpacer, outPoints)
                compZ(endSpacer, outPoints)
            elif order == 4:
                compY(endSpacer, outPoints)
                compZ(endSpacer, outPoints)
                compX(endSpacer, outPoints)
            elif order == 5:
                compZ(endSpacer, outPoints)
                compY(endSpacer, outPoints)
                compX(endSpacer, outPoints)
            elif order == 6:
                compZ(endSpacer, outPoints)
                compX(endSpacer, outPoints)
                compY(endSpacer, outPoints)
            else:
                compX(endSpacer, outPoints)
                compY(endSpacer, outPoints)
                compZ(endSpacer, outPoints)

            outPoints.append(endSpacer)
            outPoints.append(p2)

        spline = c4d.SplineObject(len(outPoints), c4d.SPLINETYPE_LINEAR)
        spline[c4d.SPLINEOBJECT_INTERPOLATION] = 1 # natural
        spline[c4d.SPLINEOBJECT_SUB] = 8
        
        for x in range(len(outPoints)):
            spline.SetPoint(x, outPoints[x])

        return spline

    def GetContour(self, op, doc, lod, bt):
        gridUnit = op[res.CONNECTION_GRID_NETWORK_CONNECTION_GRID_UNIT_LENGTH]
        order = op[res.CONNECTION_GRID_NETWORK_CONNECTION_ORDER]

        if self.INPUT_SPLINE is None: return None

        return self.MakeSpline(gridUnit, order)

    def GetVirtualObjects(self, op, hh):
        inObj = op.GetDown()
        gridUnit = op[res.CONNECTION_GRID_NETWORK_CONNECTION_GRID_UNIT_LENGTH]
        order = op[res.CONNECTION_GRID_NETWORK_CONNECTION_ORDER]

        if inObj is None: return None

        hClone = op.GetAndCheckHierarchyClone(hh, inObj, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, False)

        if not hClone['dirty']: return hClone['clone']
        if hClone['clone'] is None: return None

        self.INPUT_SPLINE = hClone['clone']
        self.UPDATE = True

        return self.MakeSpline(gridUnit, order)


if __name__ == '__main__':
    connectiongridData.Register()
