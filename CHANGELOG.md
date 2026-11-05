# Changelog

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

- Added: with ACE, link loose belts into the machine gun someone is firing, or your own, so an ammo bearer only carries belts (idea by Guide [ISO])
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
