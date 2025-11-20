
  .stack(
    s("sd ~ ~ sd ~ sd ~"),
    s("hh*7").swing(3)
  )


#*******************************

s("bd ~ bd ~ bd ~ ~")
  .stack(
    s("sd [~ sd] ~ sd ~ [sd ~]"),
    s("hh*7").gain(0.1618033).swing(0.1618033)
  )

#**********************GREAT*******

stack(
  s("~ bd ~ bd ~ bd"),
  s("sd ~ sd ~ sd ~"),
  s("hh*7").swing(3).gain(0.85)
)

#******************1/2 TINE**********

stack(
  s("~ ~ bd ~ ~ ~"),
  s("sd ~ sd ~ sd ~"),
  s("hh*7").swing(3).gain(0.85)
)

#********MORE**********************

stack(
  s("~ bd bd ~ bd ~"),
  s("sd ~ sd ~ sd ~"),
  s("hh*7").swing(3).gain(0.9)
)


#**********************************

stack(
  s("~ bd ~ ~ bd ~"),
  s("sd ~ sd ~ ~ sd"),
  s("hh*7").swing(3)
)

#***********************************

stack(
  s("bd ~ bd ~ bd bd"),
  s("sd ~ sd ~ sd ~"),
  s("hh*7").swing(3).gain(0.8)
)


#****************************************


stack(

  s("hh*7 hh*7 hh*7 hh*7").gain(0.7),


  s("bd ~ bd ~ bd bd ~ bd ~ bd bd ~ bd ~ bd bd ~ bd ~ bd bd ~ bd ~ bd bd ~ bd ~ bd bd ~ bd ~ bd bd"),


  s("sd ~ sd ~ sd sd ~ sd ~ sd sd ~ sd ~ sd sd ~ sd ~ sd sd ~ sd ~ sd sd ~ sd ~ sd sd ~ sd ~ sd")
)

#***************************************************

stack(

  // Hi-hat — use TR‑808 hi-hat
  s("hh*7 hh*7 hh*7 hh*7").bank("circuitsdrumtracks").gain(0.1111111618033),

  // Kick (BD) — use TR‑808 kick
  s("bd ~ ~ ~ bd ~ ~ ~ bd bd ~ ~ ~ bd ~ ~ ~ bd bd ~ ~ ~ bd ~ ~ ~ bd bd ~ ~ ~ bd ~ ~ ~")
    .bank("circuitsdrumtracks").gain(0.999618033),

  // Snare — use TR‑808 snare
  s("sd ~ ~ ~ sd ~ ~ ~ sd sd ~ ~ ~ sd ~ ~ ~ sd sd ~ ~ ~ sd ~ ~ ~ sd sd ~ ~ ~ sd ~ ~ ~")
    .bank("circuitsdrumtracks").gain(0.18033),

  // Add machine‑drum / extra feel — use TR‑909 or another bank
  s("bd ~ bd ~ bd bd ~ bd ~ bd").bank("circuitsdrumtracks").swing(3).gain(0.8999)

)

#************************THIS IS HOUSE******************************

stack(

  // Hi-hat — use TR‑808 hi-hat
  s("hh*7 hh*7 hh*7 hh*7").bank("bossdr110").gain(0.01111111618033),

  // Kick (BD) — use TR‑808 kick
  s("bd ~ ~ ~ ~ ~ ~ ~ bd ~ ~ ~  ~ ~ ~ ~ bd ~ ~ ~ ~ ~ ~ ~ bd  ~ ~ ~ ~~ ~ ~")
    .bank("rolandtr909").gain(0.618033),

  // Snare — use TR‑808 snare
  s("sd ~ ~ ~ sd ~ ~ ~ sd ~ ~ ~ ~ sd ~ ~ ~ ~ sd ~ ~ ~ sd ~ ~ ~ sd ~ ~ ~ ~ sd ~ ~ ~")
    .bank("akaixr10").gain(0.018033),

  // Add machine‑drum / extra feel — use TR‑909 or another bank
  s("~ ~ bd ~ bd bd ~ bd ~ ~").bank("bossdr110").swing(3).gain(0.8999)

)

#***************************ROCKKKK!!!!!POP!!!!!!**********TAYLOR*******KATY PERRY**************************


stack(

  // 4-on-the-floor KICK — 909
  s("bd ~ bd ~ bd ~ bd ~")
    .bank("rolandtr909")
    .gain(0.75),

  // House hi-hats — DR110 (alternating open/closed with subtle swing)
  s("hh hh hh hh oh ~ hh hh oh ~")
    .bank("bossdr110")
    .gain(0.25)
    .swing(2),

  // Snare / Clap on beats 2 & 4 — A.K.A.I. XR10
  s("~ ~ sd ~ ~ ~ sd ~")
    .bank("akaixr10")
    .gain(0.30),

  // Extra groovy machine-drum ghost notes — DR110
  s("~ ~ ~ bd ~ bd ~ ~ ~ bd ~ ~~ ~ bd ~")
    .bank("bossdr110")
    .gain(0.5)
    .swing(3)
)


#**********************************************************


stack(

  // 4-on-the-floor KICK — 909
  s("bd ~ bd ~ bd ~ bd ~")
    .bank("rolandtr909")
    .gain(0.75),

  // House hi-hats — DR110 (alternating open/closed with subtle swing)
  s("hh hh hh ~ oh hh hh ~ oh hh")
    .bank("bossdr110")
    .gain(0.25)
    .swing(4),

  // Snare / Clap on beats 2 & 4 — A.K.A.I. XR10
  s("~ ~ sd ~ ~ ~ sd ~")
    .bank("akaixr10")
    .gain(0.30),

  // Extra groovy machine-drum ghost notes — DR110
  s("~ ~ ~ bd ~ bd ~ ~ ~ bd ~ ~~ ~ bd ~")
    .bank("bossdr110")
    .gain(0.5)
    .swing(3)
)


#***************************1983*******************************

stack(

  // 4-on-the-floor KICK — 909
  s("bd ~ bd ~ bd ~ bd ~")
    .bank("rolandtr909")
    .gain(0.75),

  // House hi-hats — DR110 (alternating open/closed with subtle swing)
  s("hh hh ~ ~ ~ hh hh ~ oh hh")
    .bank("bossdr110")
    .gain(0.25)
    .swing(4),

  // Snare / Clap on beats 2 & 4 — A.K.A.I. XR10
  s("~ ~ sd ~ ~ ~ sd ~")
    .bank("akaixr10")
    .gain(0.30),

  // Extra groovy machine-drum ghost notes — DR110
  s("~ ~ ~ bd ~ bd ~ ~ ~ bd ~ ~~ ~ bd ~")
    .bank("bossdr110")
    .gain(0.5)
    .swing(3)
)

#***********************************************************


stack(

  // 4-on-the-floor KICK — 909
  s("bd ~ bd ~ bd ~ bd ~")
    .bank("rolandtr909")
    .gain(0.618033),

  // House hi-hats — DR110 (alternating open/closed with subtle swing)
  s("hh hh ~ ~ ~ hh hh ~ oh hh")
    .bank("bossdr110")
    .gain(0.1618033)
    .swing(4),

  // Snare / Clap on beats 2 & 4 — A.K.A.I. XR10
  s("~ ~ sd ~ ~ ~ sd ~")
    .bank("akaixr10")
    .gain(0.30),

  // Extra groovy machine-drum ghost notes — DR110
  s("~ ~ ~ bd ~ bd ~ ~ ~ bd ~ ~~ ~ bd ~")
    .bank("bossdr110")
    .gain(0.5)
    .swing(3)
)
