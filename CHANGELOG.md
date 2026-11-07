# Changelog

## 1.2.6

- Changed: the stripper clip minigame sits low on the screen, with more room between its rows; the round count is no longer cut off at the bottom
- Changed: the line saying it goes on by itself when left alone stands there all along and only lights up while it does, instead of popping up

## 1.2.5

- Changed: the stripper clip minigame sits as low as the other minigame, in place of the loading panel, and is wider, so its steps, the arrow's words and the instructions fit
- Added: without "must hit" a countdown says when the clip minigame goes on by itself, and then that it does so slower and how to go faster

## 1.2.4

- Changed: the stripper clip minigame sits just above the loading panel instead of high up the screen
- Changed: it shows what to do where to do it: the two steps at the top, a moving path of dots from the clip to the guide, and an arrow under the thumb mark that points the way to pull, with clearer instructions below
- Changed: without "must hit" it plays itself only after six seconds of doing nothing, and then slower than pressing

## 1.2.3

- Fixed: refilling from the menus with loose rounds in the inventory took the loose rounds and the round minigame even with clips and a speedloader; whole clips go first now whenever the speedloader takes them
- Added: a hint when clips go in round by round, and why (no speedloader, or the speedloader set to loose rounds only)
- Added: one line per fill in the RPT saying where the rounds came from and whether the clip minigame ran

## 1.2.2

- Changed: a new stripper clip minigame in a window of its own, played with the mouse: the magazine stands cut open with the speedloader's guide on top; drag the clip into the guide, then grab the thumb mark and pull the rounds down. Pull steadily: the spring lets them through slower the fuller the magazine, and pulled too far ahead they jam and spring back. Esc stops, what went in stays in

## 1.2.1

- Added: universal ammunition on stripper clips, and in cartons of three clips
- Added: while the speedloader speeds up loose rounds, the loading display shows its badge with how much faster, lighting up with each round, and in the minigame the round flies with a trail
- Changed: cartons of clips hold three clips (5.56x45 also two) and are named "Pack on Clips", so they sort right after the packs of loose rounds
- Changed: stripper clips are shown and hidden in ACE Arsenal together with the single rounds

## 1.2.0

- Added: a minigame for stripper clips: seat the clip in the guide as it passes over the magazine, then hold to press the rounds down, letting go before the pressure reaches the red or the clip jams
- Changed: what you drag onto a magazine is what goes in: loose rounds or a pack load only loose rounds (with the round minigame), a clip or a carton of clips only rounds on clips; the menus press in whole clips when the speedloader takes them, else loose rounds first
- Changed: packs come in 10, 30 and 60 rounds; the other sizes are hidden but still exist, so saved loadouts keep them
- Changed: cartons of clips in the sizes they are issued in: 5.56x45 2x10 and 3x10, 5.45x39, 5.8x42 and 7.62x39 2x10, 7.62x51 and 7.62x54R 4x5, 7.92x57 3x5, .303 2x5

## 1.1.3

- Added: setting "Speedloader": stripper clips only, loose rounds only (the boost from before 1.1.0) or both (default)
- Added: setting "Speedloader factor for loose rounds" (default 0.5, as before 1.1.0)
- Changed: whole stripper clips take 0.4 of the single-round time instead of 0.25

## 1.1.2

- Changed: the stripper clips' pictures show the clip lying as it does in front of its carton, so clip and carton match

## 1.1.1

- Changed: the speedloader shows in the arsenal's own views (rounds, packs, belts), and among the fitting ammunition while a weapon takes a caliber that comes on stripper clips

## 1.1.0

- Added: stripper clips for the calibers issued on them (5.56x45, 5.45x39, 5.8x42 and 7.62x39 on 10-round clips, 7.62x51, 7.62x54R, 7.92x57 and .303 on 5-round clips), in every variant, and cartons of three clips
- Added: strip a clip into loose rounds from its context menu or the ACE "Unpack" menu; a carton of clips unpacks into clips
- Added: rounds on clips count as ammunition for loading; drag a clip or a carton of clips onto a magazine to load it
- Changed: the speedloader now loads a whole stripper clip at once, at a quarter of the time of single rounds ("Stripper clip loading factor"); it no longer speeds up loose rounds

## 1.0.3

- Fixed: items on the ground sank in and tilted, cut off at the ground; every ground model has a geometry LOD now, so it rests flat
- Changed: the cartons on the ground have the colours of their inventory picture, no longer darker, and their tuck flaps are the carton's own colour

## 1.0.2

- Changed: the packs' cartons on the ground are printed paperboard now: board grain, rounded and rubbed edges, knocked corners, the tuck flaps in relief, a barcode and lot print on the back, a matte material with a normal map
- Added: the cartons cast shadows

## 1.0.1

- Changed: packs on the ground are now the carton from their inventory picture, with the same colour, print, coloured band and flap, for every caliber and variant, in three sizes

## 1.0.0

First release on the Steam Workshop. Everything below led up to it.

- Fixed: a minigame reward and the streak shared one line and ran out of the loading display; the reward now shows on its own for its moment

## 0.1.44

- Fixed: the round floated beside the right hand's fingers; it goes by the hand's own frame now, measured in the game, so it lies between thumb and index finger
- Fixed: the right hand stopped above the magazine; it reaches it now, and the round goes into the slot under its fingers

## 0.1.43

- Fixed: the right hand pressed the round in beside the magazine; it aims at the magazine as it is held now, and the round comes over to the held magazine's top as it goes in, whatever magazine it is

## 0.1.42

- Fixed: the round floated below the right hand's fingers; it hangs on the right hand itself now

## 0.1.41

- Changed: the left hand's fingers lie together around the magazine instead of spread
- Added: the right hand takes a round between thumb and index finger at the pouch, carries it up and presses it into the magazine from above, where it goes

## 0.1.40

- Added: streak rewards in the minigame. From x5 on, every 2 hits throw in 1 to 3 random extra rounds, at x15 the magazine in hand fills at once; all of it adjustable in the CBA settings (Minigame) and can be switched off

## 0.1.39

- Changed: unloading sounds like rounds falling and bouncing, from studio recordings of cartridge cases on concrete (BigSoundBank, CC0)

## 0.1.38

- Changed: new sounds for a round going in, taking the magazine and a full magazine, cut from a real recording of a magazine being loaded (BigSoundBank "Gun, loading #4", CC0); with and without ACE alike

## 0.1.37

- Fixed: the minigame's round flies from left to right again

## 0.1.36

- Changed: new ground models: a printed carton with label, tape and stencilling, a round shaped like one (rim, groove, shoulder, neck, ogive), a belt with its links, a ribbed speedloader
- Fixed: items floated above the ground; they are centred like the game's own now
- Changed: the minigame's round flies in from the right and the magazine on the track has to catch it; the rounds no longer stack in the opening

## 0.1.35

- Fixed: a magazine whose model has a geometry of its own (the CAR-95's) shoved the unit across the map while loading
- Fixed: items on the ground stood on end; they lie flat now, and every model has a material, so it is lit like the game's own
- Changed: the minigame's opening is the magazine again, shaped like a round, and the rounds of the run stand in it
- Added: a streak beside the count that grows louder the longer the run: Nice, On fire, Unstoppable

## 0.1.34

- Added: views at the top of ACE Arsenal's sort list in the ammunition tab: fitting ammunition (default), rounds only, boxes only, belts only
- Added: "Universal ammunition" server setting, on by default; off hides it and nothing loads from it
- Added: "Loading display" setting: the panel (default) or the original GreenMag's hold ring, without minigame
- Added: models for rounds, boxes, belts and the speedloader lying on the ground
- Changed: the original's boxes of 10 to 60 rounds are back beside the real ones
- Changed: more room in the loading display; the minigame's opening is a straight band with bright edges

## 0.1.33

- Changed: packs come in the sizes the real cartridges are boxed in: 50 for pistol rounds, 20 for rifle rounds (5.45 in 30, 5.56 also as 30 on stripper clips, 7.92 in 15), 10 for the large calibers, 5 and 25 for shotgun shells
- Changed: "Only ammunition in use" also hides kinds no loaded magazine has, like subsonic or Mk 262, and belts where no weapon is belt-fed
- Changed: new stand-in magazines for weapons without a magazine model of their own: pistol, rifle, AK, battle rifle, sniper, .50 and shotgun, each in the size of its magazine, with ribs, floor plate, feed lips and the top round, and an ammunition box with its belt

## 0.1.32

- Changed: the line saying what to press sits inside the loading display, the minigame's run of hits beside the count

## 0.1.31

- Fixed: the MK200's box showed an MX SW magazine in the hand
- Fixed: ACE Arsenal coloured belts for weapons that only take loose rounds, and rounds and packs for belt-fed ones

## 0.1.30

- Changed: the magazine further into the fingers
- Fixed: the minigame's line spoke of loading while unloading

## 0.1.29

- Added: "Only calibers in use" setting, on by default: ACE Arsenal lists only ammunition that a magazine of the loaded mods takes

## 0.1.28

- Fixed: the line below the loading display was cut off
- Changed: the magazine a little further towards the fingertips
- Changed: the weapon always goes away while loading, the setting for it is gone
- Changed: every kind of belt has its own picture, with its own rounds and links to fit them

## 0.1.27

- Changed: the minigame is on by default and a server setting; the round flies along a track and the magazine is the slot to hit
- Added: "Without a press" setting: the round loads anyway so nobody has to play, or nothing goes in until it is hit
- Changed: the loading display in the look of Arma Inventory Overhaul, with round corners
- Changed: "Enable the mod" stands above every other setting

## 0.1.26

- Changed: the magazine sits deeper in the hand
- Fixed: the magazine sat about 2 cm in front of the place the hand closes around

## 0.1.25

- Changed: an own display replaces the ring and the bar while loading: the magazine, its count and one segment for each of its rounds, lighting with each click
- Added: "Loading minigame" setting, off by default
- Changed: the hand a little closer around the magazine

## 0.1.24

- Changed: a pack's rounds go where the pack was, only what has no room there goes elsewhere

## 0.1.23

- Changed: the magazine in the hand sits further forward and is turned a little more towards the front
- Changed: one click for every round, in step with a new counter and the ring or bar; the click climbs as the spring tightens
- Changed: every action has its own sound, all real recordings of the game, with ACE its recorded magazine sounds
- Added: "Round counter" setting
- Changed: new icons in the ACE menu
- Changed: every kind of ammunition has its own pack picture
- Added: "Open packs first" setting, on by default: a pack dragged onto a magazine has to be opened first
- Added: settings for what the ammunition tab of ACE Arsenal shows: belts and packs on, single rounds off

## 0.1.22

- Added: with ACE, link loose belts into the machine gun someone is firing, or your own, so an ammo bearer only carries belts (idea by Guide)
- Added: split a loose belt in two, in the inventory's context menu and the ACE menu

## 0.1.21

- Fixed: wrist, fingers and thumb stay within what human joints can do; the magazine lies in the palm with the thumb on one side and the fingers on the other
- Fixed: the right arm no longer hangs in the air with a kinked wrist

## 0.1.20

- Fixed: the hand is solved against the game's own hand and magazine models instead of a box: the fingers lie together and go around the magazine's front, and the hand sits closer

## 0.1.19

- Changed: the left hand holds the magazine as in a real loading grip: it comes along the magazine from behind its back, the fingers wrap around its front, the thumb lies on the near side, and the upper half stays free

## 0.1.18

- Fixed: a gap between the fingers and the magazine, the hand now closes on it and the fingertips go further around its front

## 0.1.17

- Fixed: the fingers went through the magazine; the hand is now solved against the magazine's shape and goes around it, the back in the palm, the fingers over its far side and front, the thumb on its near side
- Fixed: curved magazines stand straight in the hand, and every magazine lies against the palm whatever its depth

## 0.1.16

- Fixed: the magazine in the hand stands across the body as when really loading one, instead of turned by 90 degrees
- Fixed: the left hand closes around the magazine, palm on its broad side, fingers around its front edge, thumb behind

## 0.1.15

- Changed: ACE is optional. Without it everything works through dragging and the inventory's context menu; with ACE its menu is there as before
- Added: refill, unload, pack rounds, take belts apart and combine them in the inventory's context menu

## 0.1.14

- Changed: the left hand holds the magazine upright, thumb up, and the magazine is turned to fit it
- Changed: the magazine in the hand is the magazine's own model wherever it has one
- Removed: the sort of the ammunition tab in ACE Arsenal
- Added: ammunition that fits one of your weapons stands out in that tab, with its own setting

## 0.1.13

- Fixed: the magazine floated above the hand during the loading animation, its place is now measured in the game
- Fixed: the right hand now presses on the magazine's top instead of in front of it
- Fixed: a warning about the inventory display on every start

## 0.1.12

- Added: the sort "Current weapon first" in the ammunition tab of ACE Arsenal

## 0.1.11

- Fixed: the magazine in the hand stands upright and sits at the left hand
- Changed: other players see the magazine too

## 0.1.10

- Fixed: the fingers now curl the right way, measured on a grip pose of the game
- Fixed: the magazine in the hand follows the hand's actual position
- Changed: single rounds and the speedloader are smaller in their pictures, without a light edge
- Added: universal rounds, packs and belts that fit every magazine, also of mods without a compat
- Added: the "Ammo rules" setting names the caliber of a mod's magazines

## 0.1.9

- Fixed: fingers bent outward in the loading animation, the hands were turned the wrong way round
- Fixed: the magazine sat below the hand during the loading animation
- Changed: the ammunition tab in ACE Arsenal sits directly below the magazines
- Changed: belt pictures are smaller and have no light edge

## 0.1.8

- Changed: another kind of round only goes into a completely empty magazine, which becomes that kind's magazine; with rounds inside only the right kind fits
- Added: an ammunition tab in ACE Arsenal
- Changed: the weapon is put away the way ACE does it
- Fixed: the magazine sat too low during the loading animation

## 0.1.7

- Changed: a magazine takes any round of its caliber, tracer into ball for one
- Fixed: a slung weapon flew off during the loading animation
- Fixed: the magazine sat below the hand during the loading animation
- Changed: the speedloader's picture shows a real stripper clip and guide

## 0.1.6

- Changed: rounds rendered anew corner to corner with brushed metal and a visible base
- Changed: belts rendered anew with M13 style links

## 0.1.5

- Fixed: the loading gesture did not play
- Changed: a magazine in the hand instead of a pouch, with shapes for rifle, AK, pistol and machine gun magazines

## 0.1.4

- Added: a loading animation with the magazine in the left hand, standing and kneeling, with its own setting

## 0.1.3

- Changed: dragging ammunition onto a magazine closes the inventory and uses the same action as the ACE menu
- Changed: the hold action shows the magazine's picture, smaller and inside the ring
- Added: own sounds for each round going in or out, belts and a finished magazine

## 0.1.2

- Added: drag rounds, a pack or a belt onto a magazine in the inventory to load it ("Drag to load" setting)
- Changed: item pictures rendered anew at twice the size, lit like product photos

## 0.1.1

- Fixed: refilling stopped with a script error when the first container held none of the rounds
- Added: "Hold to load" setting; off starts once from the menu and Esc cancels
- Changed: rendered, realistic item pictures, one per caliber and type

## 0.1.0

First version, written from scratch.
