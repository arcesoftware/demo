// =======================
// Knight Rider Theme VOXCHOP2
// =======================

// Lead riff: iconic motif (synth)
LEAD: note("e4@8 g4@8 f4@8 e4@8 c4@8 d4@8 e4@8") // repeating motif
  .sustain(0.25)
  .sound("z_sine,  gm_violin")
  .coarse(1.5)        // slight detune for richness
  .decay(0.15)
  .lpf(1200)
  .hpf(100)
  .vibrato(0.01618033, 5)
  .gain(1.618033)
  .delay(0.16158033)
  .room(0.618033)
  .loopAt(8)
  ._punchcard({width: 400})

// Bassline: driving arpeggio pattern
BASSLINE: note("e2@4 b2@4 c3@4 g2@4")  
  .struct("x*16")
  .sustain(0.2)
  .sound("gm_drawbar_organ, tri")
  .coarse(2)
  .decay(1.618033)
  .lpf(800)
  .hpf(50)
  .gain(1.618033)
  .loopAt(4)
  ._punchcard({width: 400})



// Drums: simple pulse beat
DRUMS: s("bd bd bd bd")
  .bank("akailinn")
  .postgain(1.618)
  .gain(0.1618033)

// Optional ambient VOX layer
VOX: s("gm_bassoon:<0 1>")
  .fit()
  .chop(64)
  .cut(1)
  .loopAt(16)
  .postgain(3.5)
  .gain(0.0618033)
  ._scope({ width: 1200 })
