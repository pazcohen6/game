python minimum version 3.6
tcod minimum version 

cradit to Roguelike Tutorials : https://rogueliketutorials.com/tutorials/tcod/v2/

keybind :
moment in 8 directions :
numpad :
7	8	9	↖ ↑ ↗
4		6	←	→
1	2	3	↙ ↓ ↘

stay (skip a turn):
numpad : 5

massage log : v
scroll massage log by 1 : up arrow / down arrow
scroll massage log by 10 : page up / page down  

pickup item : g

inventory : i - open the inventory
	then latter from a to z

drop item : d
	then latter from a to z

select tile : / or / (numpad divide)
	can move the selected tile with the mouse or numpad,
	numpad + shift : move 5 tiles
	numpad + ctrl : move 10 tiles
	numpad + alt : move 20 tiles

use stairs : = or u

changes :
 - Fireblall -> Firecube : euclidean distance [sqr(x^2 + y^2)] -> L1 [|x| + |y|]
 - Random tile deviation for floor tile

12/06/2025
- New Feature:
    - Critical Chance System Overhaul:
    	- All creatures (players and enemies) now have a critical chance stat.
		- During damage calculation (based on sigmuid function):
			The effective critical chance is calculated using a sigmoid-based function:
				cc = attacker_crit−target_crit
				critical_chance =  100 / (1 + math.exp(-0.03 * (cc - 55))) 
			if the roll >= 100 - critica_chance, the attack is a critical hit.
			Critical hit deals double damage.

- Stat Changes:
    - Strength now adds +5 HP per point. Every 5 points in Strength also grant +1 Attack Damage.
    - Agility now adds +2 Critical Chance per point. Every 5 points in Agility also grant +1 Defense.

- Balance Changes:
	- Health Potion : now heal 6 HP insted of 4.
