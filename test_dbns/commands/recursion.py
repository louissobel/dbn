// basic test of commands.
// recursion!


Command Rectangle L B R T {
  Line L B R B
  Line R B R T
  Line R T L T
  Line L T L B
}

Command RectInRect L B R T S {
    Rectangle L B R T

    Smaller? L R {
        RectInRect (L + S) (B + S) (R - S) (T - S) S
    }
}

Paper 0
RectInRect 30 40 60 70 3
