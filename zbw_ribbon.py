import maya.cmds as cmds
import zbw_rig as rig
import zbw_window as win
import maya.OpenMaya as om

class RibbonUI(win.Window):
	def __init__(self):
		super(RibbonUI, self).__init__()

	def commonUI(self):
		pass

	def customUI(self):
		self.widgets["ribbonNameTFG"] = cmds.textFieldGrp(l="Ribbon Name", tx="ribbon")
		self.widgets["divisionsIFG"] = cmds.intFieldGrp(l="Number of Divisions (odd nums work best)", v1=5)
		self.widgets["fkSetupCB"] = cmds.checkBox(l="Setup FK Controls", v=1)
		self.widgets["heightFFG"] = cmds.floatFieldGrp(l="Ribbon Height", v1=10.0)
		self.widgets["ratioFFG"] = cmds.floatFieldGrp(l="Heigth/width Ratio", v1=5)
		cmds.text("add more stuff about ribbon shape here")
		#axis for nurbs plane
		#option for making (or not) control structure

	def action(self, close, *args):
		#do the action here
		self.createRibbon()

		#close window
		if close:
			self.closeWindow()
		pass

	def printHelp(self, *args):
		#########  modify for inheritence ###########
		print("this is your help, yo")

	def resetValues(self, *args):
		#########  modify for inheritence ###########
		print("test values reset")

	def saveValues(self, *args):
		#########  modify for inheritence ###########
		print("test save values")

	def loadValues(self, *args):
		#########  modify for inheritence ###########
		print("test load values")

	def createRibbon(self, *args):
		self.name = cmds.textFieldGrp(self.widgets["ribbonNameTFG"], q=True, tx=True)
		self.numDiv = (cmds.intFieldGrp(self.widgets["divisionsIFG"], q=True, v=True)[0]) -1
		self.fk = cmds.checkBox(self.widgets["fkSetupCB"], q=True, v=True)
		self.height = cmds.floatFieldGrp(self.widgets["heightFFG"], q=True, v1=True)
		self.ratio = cmds.floatFieldGrp(self.widgets["ratioFFG"], q=True, v1=True)
		self.ribbonName = "%s_ribbonGeo"%self.name
		self.numJoints = self.numDiv
		self.follicleList = []
		self.follicleJntList = []

#-------make sure the num of divisions is at least 1
#-------option to use my own surface?
		#print(self.name, self.numDiv, self.fk)
		width = self.height/self.ratio
		#create the nurbsPlane
		cmds.nurbsPlane(ax=[0, 0, 1], w=width, lr=self.ratio, d=3, u=1, v=self.numDiv, ch=0, n=self.ribbonName)
#-------look into whether this is the best reuild (xtra cvs next to end)
		cmds.rebuildSurface (self.ribbonName, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=1, du=1, sv=self.numDiv, dv=3, tol=0.1, fr=0, dir=0)
		cmds.move(0, self.height/2, 0, self.ribbonName)
		cmds.xform(self.ribbonName, ws=True, rp=[0, 0, 0])

		#create the follicles on the surface

		#find the ratio for the uv's (one dir will be .5, the other a result of the num joints)
		factor = 1.0/self.numJoints

#-------create follicle group and put each follicle in there
#-------keep follicle joints separate, not parente under each follicle, separate group for those
#-------follicle jnts each go under a ctrl (star) that is under a group. That group gets parent constrained to the follicles
		for x in range (self.numJoints+1):
			Vval = x * factor
			folName = "%s_follicle%s"%(self.name, x)
			follicle = rig.follicle(self.ribbonName, folName, 0.5, Vval)[0]
			print(follicle)
			self.follicleList.append(follicle)

			#create joint and parent to follicle
			jointName = "%s_fol%s_JNT"%(self.name, x)
			#---------eventually have to figure out how to orient this correctly (use local rotate axis to match follicle?)
			folPos = cmds.xform(follicle, q=True, ws=True, t=True)
			folJoint = cmds.joint(n=jointName, p=folPos)
			self.follicleJntList.append(folJoint)

		#now create the control structure for the ribbon
		basePosRaw = cmds.xform(self.follicleJntList[0], ws=True, q=True, t=True)
		topPosRaw = cmds.xform(self.follicleJntList[self.numJoints], ws=True, q=True, t=True)
		baseVec = om.MVector(basePosRaw[0], basePosRaw[1], basePosRaw[2])
		topVec = om.MVector(topPosRaw[0], topPosRaw[1], topPosRaw[2])

		midVec = (baseVec + topVec)/2

		#-------create some options with switches for how things aim, etc at each other
		#create ctrl structure
		# structure looks like -- 1. topGrp, 1+a.base_constrainGrp, 1+b.up_Loc, 1+a+1.baseCtrl, 1+a+1+1. baseJnt
		prefixList = ["base", "mid", "top"]
		groupList = []
		vecList = [baseVec, midVec, topVec]
		locList = []
		upLocList = []
		ctrlList = []
		ctrlJntList = []

		#for each of "base", "mid", "top" create the control structure
		for i in range(3):
			groupName = "%s_%s_GRP"%(self.name, prefixList[i])
			groupList.append(groupName)

			vecName = "%sVec"%prefixList[i]
			vecList.append(vecName)

			#create group
			cmds.group(empty=True, n=groupName)
			cmds.xform(groupName, ws=True, t=[vecList[i][0], vecList[i][1], vecList[i][2]])

			#create and parent constraint locator
			locName = "%s_%s_constr_LOC"%(self.name, prefixList[i])
			locList.append(locName)

			cmds.spaceLocator(n=locName)
			cmds.xform(locName, ws=True, t=[vecList[i][0], vecList[i][1], vecList[i][2]])

			cmds.parent(locName, groupName)

			#create up locator
			upLocName = "%s_%s_up_LOC"%(self.name, prefixList[i])
			upLocList.append(upLocName)

			cmds.spaceLocator(n=upLocName)
			cmds.xform(upLocName, ws=True, t=[vecList[i][0], vecList[i][1], vecList[i][2]-1])
			cmds.parent(upLocName, groupName)

			#create controls
			ctrlName = "%s_%s_CTRL"%(self.name, prefixList[i])
			ctrlList.append(ctrlName)

			cmds.circle(nr=(0, 1, 0), r=(self.height/10*3), n=ctrlName)
			cmds.xform(ctrlName, ws=True, t=[vecList[i][0], vecList[i][1], vecList[i][2]])
			cmds.parent(ctrlName, locName)

			#create control joints (will already be parented to ctrl)
			jntName = "%s_%s_ctrl_JNT"%(self.name, prefixList[i])
			ctrlJntList.append(jntName)

			test = cmds.joint(n=jntName, p=(vecList[i][0], vecList[i][1], vecList[i][2]))

		#now bind the nurbs geo
		cmds.select(cl=True)

		for jnt in ctrlJntList:
			cmds.select(jnt, add=True)
			cmds.select(self.ribbonName, add=True)

		cmds.skinCluster(mi=3, sw=0.5, omi=True, tsb=True, nw=1)

#-------here add in the constraints to make this work properly. . . on each control have it tell what to aim at? lock these or not (depends on whether it's FK or not?)
#-------also add in the FK option here, too. . .

		#start packaging stuff up

#-------hide the locators

		folGroup = cmds.group(empty=True, n="%s_follicles_GRP"%self.name)
		for fol in self.follicleList:
			cmds.parent(fol, folGroup)

		ctrlsGroup = cmds.group(empty=True, n="%s_ctrls_GRP"%self.name)
		for grp in groupList:
			cmds.parent(grp, ctrlsGroup)

		geoGroup = cmds.group(empty=True, n="%s_geo_GRP"%self.name)
		cmds.parent(self.ribbonName, geoGroup)
		cmds.setAttr("%s.inheritsTransform"%geoGroup, 0)

		ribbonGroup = cmds.group(empty=True, n="%s_ribbon_GRP"%self.name)
		cmds.parent(folGroup, ribbonGroup)
		cmds.parent(ctrlsGroup, ribbonGroup)
		cmds.parent(geoGroup, ribbonGroup)





def zbw_ribbon():
	ribbon = RibbonUI()