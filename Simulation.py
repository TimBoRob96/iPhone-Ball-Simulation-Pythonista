from scene import *
import sound
import random
import math as ma
import numpy as np
import motion

def Magnitude(point1,point2):
	a, b = point1
	x, y = point2	
	d = ma.sqrt((x-a)**2+(y-b)**2)		
	return d
	
def collide(ball,otherball ):
	sound.play_effect('ui:switch12')
	ball.collide = True
	otherball.collide=True
	m1 = ball.mass
	m2 = otherball.mass
	x,y =ball.position
	x2,y2 = otherball.position
	vx = ball.speed
	vy=ball.speedy

	pos1 = np.array( [ x, y ] )
	pos2 = np.array( [ x2, y2 ] )

	v1 = np.array( [ vx, vy ] )
	v2 = np.array( [ otherball.speed, otherball.speedy ] )

	normal = pos2 - pos1
	
		 # You should check this is none zero, but pre-gate conditions should prevent this
	normal_unit = normal / np.sqrt( normal.dot( normal ) )

	tangent_unit = np.array( [ -normal_unit[1], normal_unit[0] ])
	v1_normal_magnitude = np.dot( normal_unit, v1 )
	v1_tangent_magnitude = np.dot( tangent_unit, v1 )
	v2_normal_magnitude = np.dot( normal_unit, v2 )
	v2_tangent_magnitude = np.dot( tangent_unit, v2 )

	v1_prime_tangent_magnitude = v1_tangent_magnitude
	v2_prime_tangent_magnitude = v2_tangent_magnitude

	v1_prime_normal_magnitude = (v1_normal_magnitude*( m1 - m2 ) + 2*m2*v2_normal_magnitude)/( m1 + m2 )
	v2_prime_normal_magnitude = (v2_normal_magnitude*( m2 - m1 ) + 2*m1*v1_normal_magnitude)/( m1 + m2 )

	v1_prime_normal = v1_prime_normal_magnitude*normal_unit
	v1_prime_tangent = v1_prime_tangent_magnitude*tangent_unit
	v2_prime_normal = v2_prime_normal_magnitude*normal_unit
	v2_prime_tangent = v2_prime_tangent_magnitude*tangent_unit

	v1_prime = v1_prime_normal +v1_prime_tangent
	v2_prime = v2_prime_normal + v2_prime_tangent
	
	vx  = v1_prime[0]
	vy =v1_prime[1]
	ball.speed=vx
	ball.speedy=vy
	delta = ball.radius + otherball.radius
	#xx,yy=ball.position + delta*normal_unit#+(1,1)
	xx,yy=ball.position + delta*normal_unit
	otherball.position = xx,yy
	otherball.speed=v2_prime[0] 
	otherball.speedy=v2_prime[1]

#def in_contact()

class MyScene (Scene):
	def setup(self):
		#gridspacing
		grid =25
		#setup lists	
		self.paths=[]
		self.spawnpath =10
		self.balls=[]	
		#rows
		for j in range(5):
		#columns
			for i in range(7):
				ball = SpriteNode('emj:Red_Circle')
				ball.position= (160+i*grid,160 +grid*j)  #-(250,0)
				ball.radius = 12#1+i+2*j# +i*10 +j*8
				ball.path=False
				if i==2 and j==2:
					ball.radius = 30
					ball.path=False
				ball.mass=ma.pi*ball.radius*ball.radius
				ball.size=2*ball.radius,2*ball.radius
				self.add_child(ball)
				ball.last_position=0,0
				ball.held =False
				ball.speed = 0
				ball.speedy=0
				ball.bouncex = False
				ball.bouncey = False
				ball.collide=True
				self.balls.append(ball)
				ball.otherballs =self.balls.copy()
				ball.otherballs.remove(ball)
				ball.collide = False
				
		self.gravity =-0
		self.friction=(1 - 0.001)#-0.0000001**ball.mass#.998#.995
		self.wallelasticity = 0.5
		motion.start_updates()
	
	def did_change_size(self):
		pass
	
	def update(self):
		#gets gravity
		g=motion.get_gravity()
	#set ball variables	
		for ball in list(self.balls):
			dx,dy=ball.position-ball.last_position
			x,y=ball.position
			r=ball.radius
	#ball is held
			if ball.held == True: 
				ball.speed = dx
				ball.speedy=dy
				vx=0
				vy=0
			else:
				vx=ball.speed
				vy=ball.speedy	
				a,b,c =g				
				vx+=a
				vy += b#self.gravity
				
	#otherball collisions
				for otherball in list(ball.otherballs):
					if Magnitude(ball.position,otherball.position) < r+otherball.radius:
						x2,y2 = otherball.position
						r2 = otherball.radius
						
						
						collide(ball,otherball)							
						vx = ball.speed
						vy=ball.speedy
						
						
	#x boundary collisions
				if (x<0+r or x> self.size.x-r): 
						if x<r:
							x=r						
						elif x> self.size.x-r:
							x=self.size.x-r
							
						#if abs(vx)<1:
							#vx=0
						#else:
							
						vx = -vx*self.wallelasticity
						sound.play_effect('drums:Drums_01')
	#y boundary collisions
				if (y<r or y> self.size.y-r):
						if y<r:
								y =r
						elif y>self.size.y-r:
								y = self.size.y-r
						#if abs(vy)<1:
							#vy=0
						#else:
						vy = -vy*self.wallelasticity
						sound.play_effect('drums:Drums_02')		
						
	#apply friction
				vx=self.friction*vx
				vy=self.friction*vy
				
	#update position and velocity
				x+=vx
				y+=vy			
				ball.speed=vx
				ball.speedy=vy
				ball.position = x,y
				
	#leaves a trail from balls
			if self.spawnpath <0 and ball.path==True:
					path = SpriteNode('shp:Spark')
					path.position = ball.position
					self.add_child(path)
					self.paths.append(path)
					self.spawnpath =30
			else:
					self.spawnpath+=-1
			if len(self.paths) > 100:
				path = self.paths[0]
				self.paths.remove(path)
				path.remove_from_parent()
				
		#updates last position
			ball.last_position=ball.position		

	def touch_began(self, touch):
		for ball in list(self.balls):
			r=ball.radius
		#touch ball 
			if Magnitude(touch.location,ball.position)<r:
					ball.velocity =0
					ball.velocityy = 0
					ball.held = True
						
	def touch_moved(self, touch):
		for ball in list(self.balls):
			r=ball.radius
			#drag ball
			if Magnitude(touch.location,ball.position)<r:
					x,y = touch.location
					dx,dy = touch.location-ball.position
					
				#boundaries
					if x< r:
						x=r
					elif x>self.size.x-r:
							x = self.size.x-r
					if y< r:
						y=r
					elif y>self.size.y-r:
							y = self.size.y-r
					
					ball.held = True
					
					for otherball in list(ball.otherballs):
						if Magnitude(ball.position,otherball.position) < r+otherball.radius:
							collide(ball,otherball)
					ball.position = x,y
			else:
					ball.held=False
		
	def touch_ended(self, touch):
		for ball in list(self.balls):
			if ball.bbox.contains_point(touch.location):
				ball.held =False
		
if __name__ == '__main__':
	run(MyScene(), PORTRAIT, show_fps=True)
