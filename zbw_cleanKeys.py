########################
#file: zbw_cleanKeys.py
#author: zeth willie
#contact: zeth@catbuks.com, www.williework.blogspot.com
#date modified: 4/19/13
#
#notes: place in scripts folder (or other location in the sys.path) and in python tab, type "import zbw_cleanKeys;zbw_cleanKeys.cleanKeys()"
########################

import maya.cmds as cmds
from functools import partial
widgets = {}

def cleanUI(*args):
    """the UI for the clean/tangent functions"""
    if cmds.window("cleanWin", exists=True):
        cmds.deleteUI("cleanWin")
        
    widgets["win"] = cmds.window("cleanWin", w=300, h=220)
    widgets["mainCLO"] = cmds.columnLayout()
    widgets["tabLO"] = cmds.tabLayout()
    
    widgets["cleanCLO"] = cmds.columnLayout("Clean Keys")
    #some explanation
    cmds.text("Options for which keys to clean/delete:")
    cmds.separator(h=10)
    #radio button group for all selected or for hierarchy under selected
    widgets["hierarchyRBG"] = cmds.radioButtonGrp(nrb=2, l1="Selected Objs Only", l2="Hierarchy Under Selected", sl=2, cc=enableCurve)    
    #radioButtons for time (timeslider, all anim, range)
    widgets["timeRBG"] = cmds.radioButtonGrp(nrb=3,l1="Timeslider", l2="All Anim", l3="Frame Range", sl=2, cw=[(1,100),(2,75),(3,75)] ,cc=partial(enableFR, "timeRBG", "frameRangeIFG", "keepCBG"))
    #int field group for frame range
    widgets["frameRangeIFG"] = cmds.intFieldGrp(nf=2, l="Start/End", v1=1, v2=24, en=False, cal=[(1,"left"),(2,"left"),(3,"left")], cw=[(1,75),(2,75),(3,75)])


    #radio button group for nurbs curves only or for all transforms
    widgets["curvesRBG"] = cmds.radioButtonGrp(nrb=2, l1="Curves/Volume Primatives Only", l2="All DAG", sl=1, cw=[(1, 170),(2, 130)])

    cmds.separator(h=10, style="single")
    
    #area to create/keep buffer curves
    widgets["bufCBG"] = cmds.checkBoxGrp(ncb=2, l1="Buffer Original Curve", l2="Overwrite Existing Buffer", v1=1, v2=0, cw=([1, 140], [2,50], [3,100], [4,50]), cal=([1, "left"], [2,"left"], [3,"left"],[4,"left"]))

    cmds.separator(h=10, style="single")    
    #check box for singlets and couplets    
    cmds.text("Singletons have only one key. Couplets have only 2 keys")
    widgets["keepCBG"] = cmds.checkBoxGrp(ncb=2, l1="Keep Singletons", l2="Keep Identical Couplets", v1=0, v2=0)

    cmds.separator(h=10)
    widgets["cleanBut"] = cmds.button(l="Clean Animation Curves!", w=300, h=40, bgc=(.6,.8,.6), c=clean)
    
    #tab for changing all tangent types
    cmds.setParent(widgets["tabLO"])
    widgets["tangentCLO"] = cmds.columnLayout("Tangents")
    
    cmds.text("here is where I'll put the shit for tangents")
    #radioButtons for tangent type (step, linear, auto, spline)
    widgets["tangentType"] = cmds.radioButtonGrp(nrb=4, l1="Step", l2="Linear", l3="Spline", l4="Auto", sl=1, cw=[(1,50),(2,50),(3,50),(4,50)])
    #radio button group for all selected or for hierarchy under selected
    widgets["tanHierRBG"] = cmds.radioButtonGrp(nrb=2, l1="Selected Objs Only", l2="Hierarchy Under Selected", sl=2, cc=enableSelect)    
    #radioButtons for time (timeslider, all anim, range)
    widgets["tanTimeRBG"] = cmds.radioButtonGrp(nrb=3,l1="Timeslider", l2="All Anim", l3="Frame Range", sl=2, cw=[(1,100),(2,75),(3,75)],cc=partial(enableFR,"tanTimeRBG","tanFrameRangeIFG"))
    #int field group for frame range
    widgets["tanFrameRangeIFG"] = cmds.intFieldGrp(nf=2, l="Start/End", v1=1, v2=24, en=False, cal=[(1,"left"),(2,"left"),(3,"left")], cw=[(1,75),(2,75),(3,75)])
    #radioButtons for curves only or for all DAG objects
    widgets["tanCurvesRBG"] = cmds.radioButtonGrp(nrb=2, l1="Curves/Volume Primatives Only", l2="All DAG", sl=1, cw=[(1, 170),(2, 130)])
    cmds.separator(h=10)

    #Button for executing the change
    widgets["tanBut"] = cmds.button(l="Change Tangent Type!", w=300, h=40, bgc=(.6,.6,.8), c=changeTan)

    #button to SELECT those objects rather than change the tangents
    cmds.separator(h=10)
    widgets["selectBut"] = cmds.button(l="Select Objects in Hierarchy", w=300, h=20, bgc=(.8,.6,.6), c=selectHier)
    
    cmds.showWindow(widgets["win"])
    cmds.window(widgets["win"], e=True, w=300, h=220)

def enableSelect(*args):
    """when hierarchy is selected, this enables the option for curves only """
    val = cmds.radioButtonGrp(widgets["tanHierRBG"], q=True, sl=True)
    if val==2:
        cmds.radioButtonGrp(widgets["tanCurvesRBG"], e=True, en=True)
        cmds.button(widgets["selectBut"], e=True, en=True)
    else:
        cmds.radioButtonGrp(widgets["tanCurvesRBG"], e=True, en=False)
        cmds.button(widgets["selectBut"], e=True, en=False)
        
def getSliderRange(*args):
    """gets framerange in current scene and returns start and end frames"""
    #get timeslider range start
    startF = cmds.playbackOptions(query=True, min=True)
    endF = cmds.playbackOptions(query=True, max=True)
    return(startF, endF)

def enableCurve(*args):
    """when hierarchy is selected, this enables the option for curves only """
    val = cmds.radioButtonGrp(widgets["hierarchyRBG"], q=True, sl=True)
    if val==2:
        cmds.radioButtonGrp(widgets["curvesRBG"], e=True, en=True)
    else:
        cmds.radioButtonGrp(widgets["curvesRBG"], e=True, en=False)
    
def enableFR(source, intField, singles="none", *args):
    """when frame range option is selected, this activates the frame range int field group"""
    val = cmds.radioButtonGrp(widgets[source], q=True, sl=True)
    if val==3:
        cmds.intFieldGrp(widgets[intField], e=True, en=True)
        if singles:
            cmds.checkBoxGrp(widgets[singles], e=True, en=False)
    elif val==2:
        cmds.intFieldGrp(widgets[intField], e=True, en=False)
        if singles:
            cmds.checkBoxGrp(widgets[singles], e=True, en=True)
    elif val==1:
        cmds.intFieldGrp(widgets[intField], e=True, en=False)
        if singles:
            cmds.checkBoxGrp(widgets[singles], e=True, en=False)
        
def clean(*args):
    """this cleans the keyframes based on the settings in clean tab"""
    #get info from options in UI
    hier = cmds.radioButtonGrp(widgets["hierarchyRBG"], q=True, sl=True)
    timeOption = cmds.radioButtonGrp(widgets["timeRBG"], q=True, sl=True)
    singles = cmds.checkBoxGrp(widgets["keepCBG"], q=True, v1=True)
    couplets = cmds.checkBoxGrp(widgets["keepCBG"], q=True, v2=True)
    curves = cmds.radioButtonGrp(widgets["curvesRBG"], q=True, sl=True)
    startF = 0
    endF = 0
    tolerance = 0.0001
    #checking buffer settings
    buffer = cmds.checkBoxGrp(widgets["bufCBG"], q=True, v1=True)
    bufOverwrite = cmds.checkBoxGrp(widgets["bufCBG"], q=True, v2=True)    
    
    #get the selection based on the criteria above
    selection = cmds.ls(sl=True, type="transform")
    #this is the selection list to operate on
    sel = []
    if selection:
        if hier==2:
            #if hierarchy is selected, we then (and only then) have the option to choose the types we'll get
            if curves == 1:
                #filter the selection down to the new selection
                curveList = []
                for obj in selection:
                    relsSh = cmds.listRelatives(obj, ad=True, f=True, type=["nurbsCurve", "renderBox", "renderSphere", "renderCone"])
                    if relsSh:
                        for shape in relsSh:
                            curve = cmds.listRelatives(shape, p=True, f=True, type="transform")[0]
                            curveList.append(curve)
                if curveList:
                    for curve in curveList:
                        sel.append(curve)
            
                for obj in selection:
                    sel.append(obj)
                            
            elif curves == 2:
                #get transforms without filtering for curves
                dagList = []
                for obj in selection:    
                    transform = cmds.listRelatives(obj, ad=True, f=True, type="transform")
                    if transform:
                        for this in transform:
                            dagList.append(this)  

                    dagList.append(obj) 
                
                for this in dagList:
                    sel.append(this)
                    
        elif hier==1:
            for obj in selection:
                sel.append(obj)
                #print "%s is selected"%obj
        
    else:
        cmds.warning("You haven't selected any transform nodes!")
    
    if timeOption == 1:
        #get timeslider range start
        startF = cmds.playbackOptions(query=True, min=True)
        endF = cmds.playbackOptions(query=True, max=True)
    elif timeOption == 3:
        #get frame range from int field
        startF = cmds.intFieldGrp(widgets["frameRangeIFG"], q=True, v1=True)
        endF = cmds.intFieldGrp(widgets["frameRangeIFG"], q=True, v2=True)
    
    #print "The frame range is %s to %s"%(startF, endF)

    #print "this will clean keys for: %s"%sel  
    # loop through objects
    for object in sel:
        #create buffer curve
        if buffer:
            cmds.bufferCurve(object, ov=bufOverwrite)
        
        keyedAttr = []
        # find which attr have keys on them
        keyedAttrRaw = cmds.keyframe(object, q=True, name=True)
        #now fix the "object_" part to "object."
        if keyedAttrRaw:
            for oldAttr in keyedAttrRaw:
                #strip full path to object down to just obj, then use that to parse the attr name 
                onlyObject = object.rpartition("|")[2]
                newAttr = oldAttr.partition("%s_"%onlyObject)[2]
                #print "stripped attr = %s, the object I'm stripping is %s"%(newAttr, onlyObject)
                keyedAttr.append(newAttr)
                #print "object: %s    attr:%s"%(object, newAttr)
            # loop through attrs with keys
            for attr in keyedAttr:                
                for a in range(2):
                    keyList = []
                    #time range stuff, if using all anim, don't use frame range. Otherwise use startF, endF
                    if timeOption == 2:
                        keyList = cmds.keyframe(object, query=True, at=attr)
                    else:
                        keyList = cmds.keyframe(object, query=True, at=attr,time=(startF, endF))
                    #if there are keys, start the looping to check to delete them
                    if (keyList):
                        keySize = len(keyList)
                        
                        if keySize < 3:
                            if keySize < 2:
                                #currentVal = cmds.getAttr((object+"."+attr), time=keyList[0])
                                if not singles:
                                    if (timeOption!=3):
                                        #get the value
                                        val = cmds.getAttr("%s.%s"%(object, attr))
                                        #cut the key
                                        if timeOption==1:
                                            cmds.cutKey(object, at=attr, cl=True, t=(startF, endF))
                                            #set the values (to make sure it doens't drop it to zero)
                                            cmds.setAttr("%s.%s"%(object, attr), val)
                                        else:
                                            cmds.cutKey(object, at=attr, cl=True)
                                            #set the values (to make sure it doens't drop it to zero)
                                            cmds.setAttr("%s.%s"%(object, attr), val)
                            else:
                                #check for keep start end options
                                if not couplets:
                                    if (timeOption!=3):
                                        firstKey = keyList[0]
                                        secondKey = keyList[1]
                                        firstVal = cmds.keyframe(object, at=attr, query=True, time=(firstKey,firstKey), eval=True)
                                        secondVal = cmds.keyframe(object, at=attr, query=True, time=(secondKey,secondKey), eval=True)
                                        #add a check in here for keep first keep last
                                        if (abs(firstVal[0]-secondVal[0])<tolerance):
                                            if timeOption==1:
                                                cmds.cutKey(object, at=attr, cl=True, t=(startF, endF))
                                                cmds.setAttr("%s.%s"%(object, attr), firstVal[0])
                                            else:
                                                cmds.cutKey(object, at=attr, cl=True)
                                                cmds.setAttr("%s.%s"%(object, attr), firstVal[0])
                        else:
                            #start with second key and compare until second to last
                            #USE DIFFERENCE VALUE
                            for i in range(1,keySize-1):

                                thisKey = keyList[i]
                                prevKey = keyList[i-1]
                                nextKey = keyList[i+1]
                                thisVal = cmds.keyframe(object, at=attr, query=True, time=(thisKey,thisKey), eval=True)
                                prevVal = cmds.keyframe(object, at=attr, query=True, time=(prevKey,prevKey), eval=True)
                                nextVal = cmds.keyframe(object, at=attr, query=True, time=(nextKey,nextKey), eval=True)
                                #accounting for floating point errors
                                prevDiff = abs(thisVal[0]-prevVal[0])
                                nextDiff = abs(thisVal[0]-nextVal[0])
                                if (prevDiff<tolerance) and (nextDiff<tolerance):
                                    cmds.cutKey(object, at=attr, time=(thisKey,thisKey), cl=True) 
                    else:
                        #print "%s had no keys on %s"%(object, attr)
                        pass
                        
                    #print "this is loop number %s, on attr: %s"%(a, attr)
           

def changeTan(*args):
    """this changes the tangent types of the objects based on settings in the tangent tab"""
    #get selected objects
    hier = cmds.radioButtonGrp(widgets["tanHierRBG"], q=True, sl=True)
    curves = cmds.radioButtonGrp(widgets["tanCurvesRBG"], q=True, sl=True)
    
    selection = cmds.ls(sl=True, type="transform")
    #this is the selection list to operate on
    sel = []
    if selection:
        if hier==2:
            #if hierarchy is selected, we then (and only then) have the option to choose the types we'll get
            if curves == 1:
                #filter the selection down to the new selection
                curveList = []
                for obj in selection:
                    relsSh = cmds.listRelatives(obj, ad=True, f=True, type=["nurbsCurve", "renderBox", "renderSphere", "renderCone"])
                    if relsSh:
                        for shape in relsSh:
                            curve = cmds.listRelatives(shape, p=True, f=True, type="transform")[0]
                            curveList.append(curve)
                if curveList:
                    for curve in curveList:
                        sel.append(curve)
                            
            elif curves == 2:
                #get transforms without filtering for curves
                dagList = []
                for obj in selection:    
                    transform = cmds.listRelatives(obj, ad=True, f=True, type="transform")
                    if transform:
                        for this in transform:
                            dagList.append(this)  
                    #add in the object itself
                    dagList.append(obj) 
                
                for this in dagList:
                    sel.append(this)
                    
        elif hier==1:
            for obj in selection:
                sel.append(obj)
        
    else:
        cmds.warning("You haven't selected any transform nodes!")
    #get framerange
    rangeRaw = cmds.radioButtonGrp(widgets["tanTimeRBG"], q=True, sl=True)
    if rangeRaw==1:
        startF = cmds.playbackOptions(query=True, min=True)
        endF = cmds.playbackOptions(query=True, max=True)
    if rangeRaw==3:
        startF = cmds.intFieldGrp(widgets["tanFrameRangeIFG"], q=True, v1=True)
        endF = cmds.intFieldGrp(widgets["tanFrameRangeIFG"], q=True, v2=True)
    #get tangent type
    tanNum = cmds.radioButtonGrp(widgets["tangentType"], q=True, sl=True)
    if tanNum==1:
        tanType = "step"
    elif tanNum==2:
        tanType = "linear"
    elif tanNum==3:
        tanType = "spline"
    elif tanNum==4:
        tanType = "auto"
        
    #for keys in range, change tangent type (don't use frame range if rangeRaw==2
    for obj in sel:
        if rangeRaw==2:
            if tanNum==1:
                cmds.keyTangent(obj, ott="step")
            else:
                cmds.keyTangent(obj, ott=tanType, itt=tanType)
        else:
            if tanNum==1:
                cmds.keyTangent(obj, ott="step", t=(startF,endF))
            else:
                cmds.keyTangent(obj, ott=tanType, itt=tanType, t=(startF,endF))

def selectHier(*args):
    """this selects the objects based on the filters in the tangents tab"""
    #get selected objects
    hier = cmds.radioButtonGrp(widgets["tanHierRBG"], q=True, sl=True)
    curves = cmds.radioButtonGrp(widgets["tanCurvesRBG"], q=True, sl=True)
    
    selection = cmds.ls(sl=True, type="transform")
    #this is the selection list to operate on
    sel = []
    if selection:
        if hier==2:
            #if hierarchy is selected, we then (and only then) have the option to choose the types we'll get
            if curves == 1:
                #filter the selection down to the new selection
                curveList = []
                for obj in selection:
                    relsSh = cmds.listRelatives(obj, ad=True, f=True, type=["nurbsCurve", "renderBox", "renderSphere", "renderCone"])
                    if relsSh:
                        for shape in relsSh:
                            curve = cmds.listRelatives(shape, p=True, f=True, type="transform")[0]
                            curveList.append(curve)
                if curveList:
                    for curve in curveList:
                        sel.append(curve)
                            
            elif curves == 2:
                #get transforms without filtering for curves
                dagList = []
                for obj in selection:    
                    transform = cmds.listRelatives(obj, ad=True, f=True, type="transform")
                    if transform:
                        for this in transform:
                            dagList.append(this)  
                    #add in the object itself
                    dagList.append(obj) 
                
                for this in dagList:
                    sel.append(this)
                    
        elif hier==1:
            for obj in selection:
                sel.append(obj)
                
        #now select
        cmds.select(cl=True)
        cmds.select(sel)
        
    else:
        cmds.warning("You don't have any transforms selected!")
    
def cleanKeys(*args):
    cleanUI()