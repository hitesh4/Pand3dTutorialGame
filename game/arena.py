from panda3d.core import(
	AmbientLight,
	PerspectiveLens,
	DirectionalLight)


class Arena:
	def __init__(self, arenaNr):
		arenaPath = "levels/arena{}/".format(arenaNr)
		self.arena = loader.loadModel(arenaPath+"arena")
		self.arena.setScale(2)
		self.arena.reparentTo(render)
		self.arena.hide()
		ambientLight = AmbientLight("ambient_light")
		ambientLight.setColor((0.2,0.2,0.2,1))
		self.alnp = render.attachNewNode(ambientLight)
		sun = DirectionalLight("sun")
		sun.setColor((1,1,1,1))
		sun.setScene(render)
		self.sunNp = render.attachNewNode(sun)
		self.sunNp.setPos(-10,-10,-10)
		self.sunNp.lookAt(0,0,0)

	def start(self):
		self.arena.show()
		render.setLight(self.alnp)
		render.setLight(self.sunNp)

	def stop(self):
		self.arena.hide()
		render.clearLight()	

	def getStartPos(self, charNr):
		if charNr == 1:	
			return self.arena.find("**/StartPosA").getPos() * 2
		elif charNr == 2:
			return self.arena.find("**/StartPosB").getPos() * 2
		else:
			return (0,0,0)
