// ===================================
// ✨ Optimized Rock Band Arrangement (Your Mix)
// ===================================

// --- 🎸 RHYTHM GUITAR (Power Chords - Lighter Drive) ---
// Adding sustain, distortion, and filtering for a defined power chord sound.
GUITAR_RHYTHM: note("<e2 d2 c2 g2>@4")
  .struct("x*4")
  .sustain(0.18) // Add back sustain for a short, punchy chord
  .sound("saw")
  .distort(0.4) // Light drive for rock texture
  .lpf(1800)
  .gain(0.618033)
  .loopAt(4)

// --- 🎹 LEAD SYNTH (Iconic Riff - Clearer Tone) ---
// The main melody, carefully filtered for clarity.
LEAD: note("e4@8 g4@8 f4@8 e4@8 c4@8 d4@8 e4@8")
  .struct("x*8")
  .sustain(0.25)
  .sound("gm_synth_brass_1, saw")
  .lpf(2000) // Clear, bright tone
  .vibrato(0.01, 5)
  .delay(0.1) // Short delay for space
  // NOTE: Your gain is very low. Adjust this if you want the lead to be heard:
  // gain(0.0618033) // If you want it barely audible
  .gain(0.818033) // <--- RECOMMENDED: Set to 0.8 to make it the clear melody
  .loopAt(8)



// --- 🎧 BASSLINE (Classic British Rock Bass) ---
// A tight, rhythmic pattern that walks between the chord tones,
// inspired by bands like The Who or Led Zeppelin.
BASSLINE: note("e2@4 e2@8 g2@8 a2@4 c3@4 g2@4") // Rhythmic pattern following the chord changes
  .struct("x*8")
  .sustain(0.2) // Short sustain for a tight, punchy fingerpicked sound
  .sound("gm_electric_bass_finger") // Classic, warm electric bass tone
  .lpf(600) // Focus on the midrange thump
  .hpf(30)
  .distort(0.1618033) // Light distortion for amp warmth/growl
  .gain(1.618033) // Solid presence in the mix
  .loopAt(4) // Loops over the 4-chord progression

// --- 🌌 PAD (Sustained Atmosphere - Cinematic Texture) ---
// Using the unique FX sound and increasing sustain for a sustained texture.
PAD: note("e3@4 g3@4 c4@4 g3@4")
  .struct("x*4")
  .sustain(3.8) // Long sustain for ambient pad
  .sound("gm_fx_soundtrack")
  .room(0.5) // Ambient reverb for the background
  .gain(0.518033)
  .loopAt(4)


// --- 🥁 DRUMS (Rock Beat - Punchier, less overpowering) ---
// Using your preferred bank for a driving, electronic rock beat.
DRUMS: s("bd(1,3) bd(2,4) sn bd bd sn")
  .bank("circuitsdrumtracks")
  .delay(0.01)
  .room(0.05)
  .gain(0.718033)
  .loopAt(1)
