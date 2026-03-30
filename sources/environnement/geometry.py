#Projet : The Descent
#Auteurs : Ahmed-Adam REZKALLAH, Noé SAMUEL, Clément Roux--Bénabou

from utils import *
from random import randint as ri
from typing import Self

class Line:
    def __init__(self,pa:Point,pb:Point,correct:Point):
        self.dx,self.dy=pb[0]-pa[0],pb[1]-pa[1]
        self.pap=self.get_p(pa)
        self.correct=self.get_p(correct)>self.pap
    
    def get_p(self,point:Point):
        if self.dx==0:
            return point[0]
        elif self.dy==0:
            return point[1]
        return point[1]-self.dy/self.dx*point[0]

    def get_correct(self,point:Point):return (self.get_p(point)>self.pap)==self.correct or self.get_p(point)==self.pap

class Triangle:
    def __init__(self,*points:Point):
        self.points = points
        self.lines = [
            Line(*(points[0:3])),
            Line(*(points[-1],*points[:2])),
            Line(*(*points[-2:],points[0]))
        ]
    
    def collidepoint(self,point:Point):return all([line.get_correct(point) for line in self.lines])
    
    def collidetriangle(self,triangle:Self):
            return any(self.collidepoint(p) for p in triangle.points) or any(triangle.collidepoint(p) for p in self.points)

Hitbox=list[Triangle]
