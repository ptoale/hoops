#!/usr/bin/env python
import math
import random
import csv


VERBOSE = False

def prob(r1, r2):
    return r1*(1.-r2)/(r1*(1.-r2)+r2*(1.-r1))
    

class Outcome(object):

    def __init__(self, name):
        self.name = name
        
    def __call__(self, team1, team2):
        return NotImplementedError

class SeedOutcome(Outcome):

    def __init__(self):
        super(SeedOutcome, self).__init__('SeedOutcome')
        
    def __call__(self, team1, team2):
        return team1 if team1<team2 else team2

class RatingOutcome(Outcome):

    def __init__(self):
        super(RatingOutcome, self).__init__('RatingOutcome')
        
    def __call__(self, team1, team2):
        return team1 if team1.rating>team2.rating else team2

class RatingRandomOutcome(Outcome):

    def __init__(self, rng=None):
        super(RatingRandomOutcome, self).__init__('RatingRandomOutcome')
        self.rng = rng or random.Random()
        
    def __call__(self, team1, team2):

        p1 = team1.rating/10000.
        p2 = team2.rating/10000.
    
        p = (p1 - p1*p2)/(p1 + p2 - 2*p1*p2)
        if self.rng.random() <= p:
            return team1
        else:
            return team2

class RandomOutcome(Outcome):

    def __init__(self, rng=None):
        super(RandomOutcome, self).__init__('RandomOutcome')
        self.rng = rng or random.Random()
        
    def __call__(self, team1, team2):

        if self.rng.random() <= 0.5:
            return team1
        else:
            return team2

class Team(object):

    def __init__(self, name, region, seed, rating):
        self.name = name
        self.region = region
        self.seed = seed
        self.rating = rating
        
        self.initial_slot = None
        self.current_slot = None

    def __eq__(self, other):
        return (self.seed == other.seed) and (self.region == other.region)
        
    def __lt__(self, other):
        if self.seed == other.seed:
            if region_order[self.region] < region_order[other.region]:
                return True
            else:
                return False
        else:
            return self.seed < other.seed 

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s(name=%s, region=%s, seed=%d, rating=%d)" % (self.__class__.__name__,
                                                               self.name, 
                                                               self.region, 
                                                               self.seed, 
                                                               self.rating)

class Bracket(object):

    def __init__(self, n_teams=128):
        self.n_teams = n_teams

        self.n_rounds = int(math.ceil(math.log(self.n_teams, 2)))

        self.n_slots = int(2*self.n_teams - 1)
        self.n_rounds = int(math.ceil(math.log(self.n_teams, 2)))
        
        self.slots = {}
        for i in range(self.n_slots):
            self.slots[i] = []
                
    def fill_teams(self, filename='2014_KP_round3.csv'):

        self.teams = [None]*self.n_slots
    
        with open(filename, 'rU') as f:
            teams = csv.DictReader(f)
            for row in teams:
                if VERBOSE:
                    print row
                team = Team(row['Team'], row['Region'], int(row['Seed']), int(row['Rating']))
                self.teams[int(row['Slot'])-1] = team
        
        if VERBOSE:
            print self.teams
        
    def slot_range(self, round):
        return (int(self.n_teams/pow(2,round)), int(self.n_teams/pow(2,round-1)-1))
        
    def parent_slot(self, slot):
        return slot/2
        
    def child_slots(self, slot):
        return (2*slot, 2*slot+1)

    def round(self, slot):
        r = self.n_rounds + 1
        for i in range(1,self.n_rounds+1):
            min_slot, max_slot = self.slot_range(i)
            if min_slot <= slot and max_slot >= slot:
                r = i
                break
        return r

    def cycle(self, n_sims=1, outcome=None):
        
        for i in range(n_sims):
            self.fill_teams()
            self.resolve(outcome)
            
#        print self.slots

    def resolve(self, outcome=None):
        
        current_slot = 2
                
        while current_slot != 1:
            
            if VERBOSE:
                print "Current slot is %d" % current_slot
            
            current_round = self.round(current_slot)
            current_team = self.teams[current_slot-1]
            if current_team:

                if VERBOSE:
                    print "   %s is in this slot" % current_team
            
                opponent_slot = current_slot+1 if (current_slot%2 == 0) else current_slot-1
                opponent_team = self.teams[opponent_slot-1]
                
                if opponent_team:                
                    # we have a game to resolve
                    winner_team = current_team
                    if outcome:
                        winner_team = outcome(current_team, opponent_team)
                    
                    winner_slot = current_slot/2
                    self.teams[winner_slot-1] = winner_team
                    self.slots[winner_slot-1].append(winner_team.name)
                    current_slot = winner_slot

                    if VERBOSE:           
                        print "   Opponent slot is %d" % opponent_slot
                        print "   GAME: %s vs %s" % (current_team, opponent_team)
                        print "   %s wins and goes to slot %d" % (current_team, current_slot)
                else:
                    # we do not have a game, need to go down the other branch
                    if VERBOSE:           
                        print "   No opponent in slot %d" % opponent_slot
                    current_slot = opponent_slot
            else:
                if VERBOSE:           
                    print "   No Team in this slot, going deeper"
                current_slot *= 2

#        print self.slots

if __name__ == '__main__':
    import doctest
    doctest.testmod() 

#    outcome = SeedOutcome()
#    outcome = RatingOutcome()
    outcome = RatingRandomOutcome()
#    outcome = RandomOutcome()

    bracket = Bracket()
    nsim = 10000
    bracket.cycle(nsim, outcome=outcome)

    slot_team_count = {}
    for s,ts in bracket.slots.iteritems():
        for t in ts:

            if s not in slot_team_count:
                slot_team_count[s] = {}
        
            if t in slot_team_count[s]:
                slot_team_count[s][t] += 1
            else:
                slot_team_count[s][t] = 1
                
    for s,cs in slot_team_count.iteritems():
        print "Slot " + str(s+1).zfill(2) + ":",
        for t,c in cs.iteritems():
            slot_team_count[s][t] /= float(nsim)
        print sorted(cs.items(), reverse=True, key=lambda x:x[1])
                

