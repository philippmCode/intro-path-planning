# coding: utf-8
import random

class UniformSampler:
    """
    Implements standard uniform sampling.
    Generates random nodes and discards them if they are in collision.
    """
    def enhance(self, prm, numNodes):

        positions = []
        
        for i in range(numNodes):
            pos = prm._getRandomPosition()
            positions.append(pos)
                
        return positions


class PathLocalSampler:
    """
    Sample near the previous colliding edge to find new nodes that can help to find a path around the obstacle.
    """
    def __init__(self, sigma=8.0):
        # Bestimmt, wie nah die neuen Knoten um das Hindernis herum gestreut werden
        self.sigma = sigma 

    def enhance(self, prm, numNodes, collision_segment=None):
        positions = []
        
        # Fallback: Wenn wir noch keine Kollisionsstelle haben, 
        # füllen wir den Raum erstmal uniform auf.
        if collision_segment is None:
            for _ in range(numNodes):
                positions.append(prm._getRandomPosition())
            return positions

        # collision_segment ist ein Tupel aus zwei Koordinaten: (pos_a, pos_b)
        pos_a, pos_b = collision_segment
        
        for _ in range(numNodes):
            # 1. Wir interpolieren einen Punkt auf der kollidierenden Kante
            t = random.random()
            interp_pos = [
                pos_a[0] + t * (pos_b[0] - pos_a[0]),
                pos_a[1] + t * (pos_b[1] - pos_a[1])
            ]
            
            # 2. Wir addieren ein Rauschen hinzu, damit die neuen Knoten sich
            # um das Hindernis herum verteilen und neue Wege daran vorbei finden.
            final_pos = [coord + random.gauss(0, self.sigma) for coord in interp_pos]
            positions.append(final_pos)
            
        return positions
    