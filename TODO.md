__Timeline__

 - When, if ever, should the timeline go back to the end state?
 - should there be a reset button on the timeline?
 - timeline should somehow (red color) highlight the impact that
   each state has _as it happens_. 
 - right now, there are a lot of steps that are invisible, becauaw
   they are changing parts of the state that aren't exposed!
   Thinking about making the scrubber skip the states that have no
   visible effect, but tricky to code, and maybe not yet even possible

__Reverse Mapping__

 - Mapping from the image (with a crosshairs or something) to the responsible LOC
 - Have ideas for this so that it could be done using the same data that whatever
   is keeping track of the impact of each state needs.
 - Tricky to get right


__Ghost generalization__

 - I want to generalize the ghosting so that Pen, Set, will be able to show 
   their effects. Hm. but each of these really has no way of showing _every_
   effect it has had... only the most recent one. It that sense, is very similar
   to the _impact_ of a state mentioned above
   
__Tkinter Text Tags__

 - this will allow syntax highlighting,
 - and more importantly, effects and events on certain types of text
   (for example, number live changing with arrows <-> )
 - Also, I think COLOR should be its own tag, because it has its own effect
   But that's kind of hacky - because the only things we know are colors are
   
     - Set [DOT] [COLOR]
     - Paper [COLOR]
     - Pen [COLOR]
     
__More state display__

  - right now, the only visible state in the GUI is the pen\_color, but it would
    be really cool to show the environment stack, and the command set? that's less interesting,
    but would be really cool to be worked in in such a way such that as they define commands,
    their "toolbox" grows with those commands.
  - but with each state that is revealed, and this is where the ghost generalization comes in,
    there needs to be a way to show the change in that state, both while hovering and scrubbing
    
__Misc__

 - floats - numbers should be floats then rounded. most intuitive way about it.


