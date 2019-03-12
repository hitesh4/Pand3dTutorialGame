from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.core import (
    CollisionSegment,
    CollisionSphere,
    CollisionNode,
    KeyboardButton,
    AudioSound)

class Player(FSM):
	def __init__(self, charId, charNr, controls):
		FSM.__init__(self, "FSM-Player{}".format(charNr))
		self.charId = charId
		charPath = "characters/character{}/".format(charNr)
		self.character = Actor(
			charPath + "char", {
				"Idle":charPath+"idle",
				"Walk":charPath+"walk",
				"Walk_back":charPath + "walk_back",
				"Punch_l":charPath+"punch_l",
				"Punch_r":charPath+"punch_r",
				"Kick_l":charPath+"kick_l",
				"Kick_r":charPath+"kick_r",
				"Hit":charPath+"hit",
				"Defend":charPath+"defend",
                "Defeated":charPath + "defeated"
			})
		self.character.reparentTo(render)
		self.character.hide()
		self.walkSpeed = 2.0
		if controls == "p1":
			self.character.setH(90)
			self.leftButton = KeyboardButton.asciiKey("d")
			self.rightButton = KeyboardButton.asciiKey("f")
			self.punchLButton = KeyboardButton.asciiKey("q")
			self.punchRButton = KeyboardButton.asciiKey("w")
			self.kickLButton = KeyboardButton.asciiKey("a")
			self.kickRButton = KeyboardButton.asciiKey("s")
			self.defendButton = KeyboardButton.asciiKey("e")
		elif controls == "p2":
			self.character.setH(-90)
			self.leftButton = KeyboardButton.right()
			self.rightButton = KeyboardButton.left()
			self.punchLButton = KeyboardButton.asciiKey("i")
			self.punchRButton = KeyboardButton.asciiKey("o")
			self.kickLButton = KeyboardButton.asciiKey("k")
			self.kickRButton = KeyboardButton.asciiKey("l")
			self.defendButton = KeyboardButton.asciiKey("p")
		characterSphere = CollisionSphere(0, 0, 1.0, 0.5)
		self.collisionNodeName = "character{}Collision".format(charId)
		characterColNode = CollisionNode(self.collisionNodeName)
		characterColNode.addSolid(characterSphere)
		self.characterCollision = self.character.attachNewNode(characterColNode)
		base.pusher.addCollider(self.characterCollision, self.character)
		base.cTrav.addCollider(self.characterCollision, base.pusher)
		characterHitRay = CollisionSegment(0, -0.5, 1.0, 0, -0.8, 1.0)
		characterColNode.addSolid(characterHitRay)
		self.getPos = self.character.getPos
		self.getX = self.character.getX
		# self.characterCollision.show()

	def start(self, startPos):
		self.character.setPos(startPos)
		self.character.show()
		self.request("Idle")
		self.canBeHit = False
		self.isDefending = False
		self.health = 100
		self.gotDefeated = False
		taskMgr.add(self.moveTask, "move Task {}".format(self.charId))

	def stop(self):
		self.character.hide()
		taskMgr.remove("move Task {}".format(self.charId))
		self.ignoreAll()


	def moveTask(self, task):
		if self.gotDefeated:
			base.messenger.send("GameOver")
			return task.done

		if self.attackAnimationPlaying(): return task.cont
		speed = 0.0
		isDown = base.mouseWatcherNode.isButtonDown

		if isDown(self.defendButton):
			if self.state != "Defend":
				self.isDefending = True
				self.request("Defend")
			return task.cont

		self.isDefending = False
		isAction = False
		if isDown(self.punchLButton):
			isAction = True
			self.request("Punch_l")
		elif isDown(self.punchRButton):
			isAction = True
			self.request("Punch_r")
		elif isDown(self.kickLButton):
			isAction = True
			self.request("Kick_l")
		elif isDown(self.kickRButton):
			isAction = True
			self.request("Kick_r")
		if isAction:
			base.messenger.send("hitEnemy{}".format(self.enemyColName))
			return task.cont


		if isDown(self.leftButton):
			speed += self.walkSpeed
		if isDown(self.rightButton):
			speed -= self.walkSpeed
		yDelta = speed * globalClock.getDt()
		self.character.setY(self.character, yDelta)

		if speed != 0.0 and self.state != "Walk" and self.state != "Walk_back":
			if speed < 0:
				self.request("Walk")
			else:
				self.request("Walk_back")
		elif speed == 0.0 and self.state != "Idle":
			self.request("Idle")

		return task.cont

	def attackAnimationPlaying(self):
		actionAnimations = [
			"Punch_l",
			"Punch_r",
			"Kick_l",
			"Kick_r",
			"Hit"]
		if self.character.getCurrentAnim() in actionAnimations: return True

	def setEnemy(self, enemyColName):
		self.enemyColName = enemyColName
		inEvent = "{}-into-{}".format(enemyColName, self.collisionNodeName)
		base.pusher.addInPattern(inEvent)
		self.accept(inEvent, self.setCanBeHit, [True])
		outEvent = "{}-out-{}".format(enemyColName, self.collisionNodeName)
		base.pusher.addOutPattern(outEvent)
		self.accept(outEvent, self.setCanBeHit, [False])

	def setCanBeHit(self, yes, collision):
		eventName = "hitEnemy{}".format(self.collisionNodeName)
		if yes:
			self.accept(eventName, self.gotHit)
		else:
			self.ignore(eventName)
		self.canBeHit = yes

	def gotHit(self):
		if not self.canBeHit or self.isDefending:
			return
		self.health -= 10
		if self.health <= 0:
			self.gotDefeated = True
			self.request("Defeated")
		else:
			self.request("Hit")




	def enterIdle(self):
		self.character.loop("Idle")

	def exitIdle(self):
		self.character.stop()

	def enterWalk(self):
		self.character.loop("Walk")

	def exitWalk(self):
		self.character.stop()

	def enterWalk_back(self):
		self.character.loop("Walk_back")

	def exitWalk_back(self):
		self.character.stop()

	def enterPunch_l(self):
		self.character.play("Punch_l")

	def exitPunch_l(self):
		self.character.stop()

	def enterPunch_r(self):
		self.character.play("Punch_r")

	def exitPunch_r(self):
		self.character.stop()

	def enterKick_l(self):
		self.character.play("Kick_l")

	def exitKick_l(self):
		self.character.stop()

	def enterKick_r(self):
		self.character.play("Kick_r")

	def exitKick_r(self):
		self.character.stop()

	def enterDefend(self):
		self.character.play("Defend")

	def exitDefend(self):
		self.character.stop()

	def enterHit(self):
		self.character.play("Hit")

	def exitHit(self):
		self.character.stop()

	def enterDefeated(self):
		self.character.play("Defeated")

	def exitDefeated(self):
		self.character.stop()
