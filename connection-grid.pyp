# Copyright (C) 2019 Cody Sorgenfrey
import c4d
import os

class res(object):
    CONNECTION_GRID_NETWORK_CONNECTION_GROUP = 1000
    CONNECTION_GRID_NETWORK_CONNECTION_GRID_UNIT_LENGTH = 1001
    CONNECTION_GRID_NETWORK_CONNECTION_ORDER = 1002
    CONNECTION_GRID_NETWORK_CONNECTION_START_OBJ = 1003
    CONNECTION_GRID_NETWORK_CONNECTION_END_OBJ = 1004
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



def compX(lastIn, endSpacer, points):
    if lastIn.x != endSpacer.x:
        lastIn = c4d.Vector(endSpacer.x, lastIn.y, lastIn.z)
        points.insert( len(points)-2, lastIn )
    return lastIn

def compY(lastIn, endSpacer, points):
    if lastIn.y != endSpacer.y:
        lastIn = c4d.Vector(lastIn.x, endSpacer.y, lastIn.z)
        points.insert( len(points)-2, lastIn )

    return lastIn

def compZ(lastIn, endSpacer, points):
    if lastIn.z != endSpacer.z:
        lastIn = c4d.Vector(lastIn.x, lastIn.y, endSpacer.z)
        points.insert( len(points)-2, lastIn )
    return lastIn

class connectiongridData(c4d.plugins.ObjectData):
    PLUGIN_ID = 1053026
    PLUGIN_NAME = 'connection grid'
    PLUGIN_INFO = c4d.OBJECT_GENERATOR | c4d.OBJECT_ISSPLINE
    PLUGIN_DESC = 'Oconnectiongrid'
    PLUGIN_ICON = load_bitmap('res/icons/connection grid.tiff')
    PLUGIN_DISKLEVEL = 0
    LAST_FRAME = 0

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
        self.InitAttr(node, object, [res.CONNECTION_GRID_NETWORK_CONNECTION_START_OBJ])
        self.InitAttr(node, object, [res.CONNECTION_GRID_NETWORK_CONNECTION_END_OBJ])

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

    def GetContour(self, op, doc, lod, bt):
        startObj = op[res.CONNECTION_GRID_NETWORK_CONNECTION_START_OBJ]
        endObj = op[res.CONNECTION_GRID_NETWORK_CONNECTION_END_OBJ]
        gridUnit = op[res.CONNECTION_GRID_NETWORK_CONNECTION_GRID_UNIT_LENGTH]
        order = op[res.CONNECTION_GRID_NETWORK_CONNECTION_ORDER]

        if startObj is None or endObj is None: return None

        points = [startObj.GetMg().off, endObj.GetMg().off]

        startSpacer = snap((startObj.GetMg() * c4d.utils.MatrixMove(c4d.Vector(gridUnit, 0, 0))).off, gridUnit, False)
        points.insert( len(points)-1, startSpacer )

        endSpacer = snap((endObj.GetMg() * c4d.utils.MatrixMove(c4d.Vector(gridUnit, 0, 0))).off, gridUnit, False)
        points.insert( len(points)-1, endSpacer )

        lastIn = startSpacer

        if order == 2:
            lastIn = compX(lastIn, endSpacer, points)
            lastIn = compZ(lastIn, endSpacer, points)
            lastIn = compY(lastIn, endSpacer, points)
        elif order == 3:
            lastIn = compY(lastIn, endSpacer, points)
            lastIn = compX(lastIn, endSpacer, points)
            lastIn = compZ(lastIn, endSpacer, points)
        elif order == 4:
            lastIn = compY(lastIn, endSpacer, points)
            lastIn = compZ(lastIn, endSpacer, points)
            lastIn = compX(lastIn, endSpacer, points)
        elif order == 5:
            lastIn = compZ(lastIn, endSpacer, points)
            lastIn = compY(lastIn, endSpacer, points)
            lastIn = compX(lastIn, endSpacer, points)
        elif order == 6:
            lastIn = compZ(lastIn, endSpacer, points)
            lastIn = compX(lastIn, endSpacer, points)
            lastIn = compY(lastIn, endSpacer, points)
        else:
            lastIn = compX(lastIn, endSpacer, points)
            lastIn = compY(lastIn, endSpacer, points)
            lastIn = compZ(lastIn, endSpacer, points)

        spline = c4d.SplineObject(len(points), c4d.SPLINETYPE_LINEAR)
        for x in range(len(points)):
            spline.SetPoint(x, points[x])

        return spline

if __name__ == '__main__':
    connectiongridData.Register()
