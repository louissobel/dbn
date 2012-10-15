// basic test of commands.
// nesting!


Command Rectangle L B R T {
  Line L B R B
  Line R B R T
  Line R T L T
  Line L T L B
}

Command RectInRect H V N S {
    Repeat B 0 N {
        Set A (B * S)
        Rectangle (H-A) (V-A) (A+H) (A+V)
    }
}

Paper 0
RectInRect 50 50 25 2
