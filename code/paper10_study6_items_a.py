"""Deep paraphrases for the first 38 control parents, written under rules 1-6.

Rule 6 was the lesson of the Study 4 reading: an option naming a term is
reworded into another expression of that term, never into its definition, and a
reworded option may not borrow a content word from its own stem. So "nervous
system" becomes "the neural system" rather than "the system that carries
signals", and where no synonym exists the item is marked exempt instead of being
forced.

These are control parents. None of them is trained on, so no choice made here
can flatter the exposed group.
"""

ITEMS = {
    "arcc_test_0032": {
        "prompt": "Which of these statements correctly states a property of a kind of matter?",
        "optA": "Air consists of several gases mixed together.",
        "optB": "Ice consists of several gases mixed together.",
        "optC": "Air is in the liquid state.",
        "optD": "Ice is in the liquid state."},
    "arcc_test_0046": {
        "prompt": "Which piece of equipment is best for mapping the surface relief of "
                  "the United States?",
        "optA": "a radio-echo ranging device", "optB": "a magnetic direction finder",
        "optC": "an orbiting observation craft", "optD": "a wireless receiver"},
    "arcc_test_0081": {
        "prompt": "Certain sea creatures living far below the surface can make light of "
                  "their own. That light is most likely put to which use?",
        "optA": "travelling through the water", "optB": "making oxygen",
        "optC": "drawing in animals they eat",
        "optD": "getting away from animals that hunt them"},
    "arcc_test_0083": {
        "prompt": "Thomas Edison most likely arrived at the light bulb by using",
        "optA": "burning candles.", "optB": "models of the atom.",
        "optC": "light bounced off surfaces.", "optD": "the methods of science."},
    "arcc_test_0099": {
        "prompt": "On a sunny day a polished metal ball appears very bright. What gives "
                  "it that appearance?",
        "optA": "The ball creates light of its own.",
        "optB": "The ball throws light back.",
        "optC": "The ball takes light in and lets it out again.",
        "optD": "The ball takes light in and holds on to it."},
    "arcc_test_0104": {
        "prompt": "Students examine a patch of mold on bread using tweezers and "
                  "magnifying glasses. What else should they use to stay safe?",
        "optA": "strong lighting", "optB": "tinted eyewear",
        "optC": "respirators", "optD": "heated plates"},
    "arcc_test_0115": {
        "prompt": "An atom gains an electron. What is the result?",
        "optA": "A proton is lost from the atom.",
        "optB": "The atom pulls in further electrons.",
        "optC": "The atom's mass number rises.",
        "optD": "The atom takes on a negative charge."},
    "arcc_test_0154": {
        "prompt": "Why does a tiled floor feel colder underfoot than a carpeted one?",
        "optA": "The tile is at a lower temperature than the carpet.",
        "optB": "Heat passes more readily through tile than through carpet.",
        "optC": "Heat passes more readily through carpet than through tile.",
        "optD": "Tile holds heat back better than carpet does."},
    "arcc_test_0159": {
        "prompt": "Which of these shows a chemical change taking place?",
        "optA": "a pane of glass shattering", "optB": "a metal bin developing rust",
        "optC": "sugar going into solution in water",
        "optD": "water drying off a pavement"},
    "arcc_test_0172": {
        "prompt": "Which environmental risk is NOT connected with getting rid of used "
                  "motor oil from cars?",
        "optA": "It will not dissolve and is hard to clear away.",
        "optB": "It goes into solution in water and brings about acid rain.",
        "optC": "It reaches storm drains and fouls water at the surface.",
        "optD": "It seeps onto the land and fouls the soil and the water beneath."},
    "arcc_test_0220": {
        "prompt": "Which investigation would best test how gravity acts on objects in motion?",
        "optA": "pencils dropped from one height",
        "optB": "balloons rising from one height",
        "optC": "a bicycle gathering pace on level ground",
        "optD": "a ball losing pace on level ground"},
    "arcc_test_0222": {
        "prompt": "The Alps, the Appalachians and the Himalayas were all formed from",
        "optA": "buckling of rock layers.", "optB": "tremors of the ground.",
        "optC": "tectonic plate activity.", "optD": "glacial deposition."},
    "arcc_test_0245": {
        "prompt": "A student reads this account of a region: it has warm summers, mild "
                  "winters, and rain falling often. What does the account best tell the "
                  "student about?",
        "optA": "the weather at present", "optB": "a weather prediction",
        "optC": "the overall climate", "optD": "shifts in the climate"},
    "arcc_test_0273": {
        "prompt": "Plates of the lithosphere have shifted and built landforms on Earth's "
                  "surface. Which landform arises where plates fold over one another?",
        "optA": "a tremor of the ground", "optB": "a chain of mountains",
        "optC": "a watercourse", "optD": "an erupting peak"},
    "arcc_test_0282": {
        "prompt": "On volcanoes, what is the chief way surface rock comes into being?",
        "optA": "Molten material chills rapidly.",
        "optB": "Great pressure re-forms the crystals in rock.",
        "optC": "Rock hardens gradually far below the surface.",
        "optD": "Rock builds up from settled sediment."},
    "arcc_test_0286": {
        "prompt": "Every organism handles nutrients. Which sentence best describes "
                  "something plants and animals both do with them?",
        "optA": "Sunlight's energy makes the nutrients.",
        "optB": "Nutrients make cell walls stronger.",
        "optC": "Cells take nutrients apart into forms they can use.",
        "optD": "The digestive tract takes nutrients apart."},
    "arcc_test_0306": {
        "prompt": "The digestive system reduces food to molecules the body's cells can "
                  "use. Which other system sets the pace at which digestion proceeds?",
        "optA": "the cardiovascular system", "optB": "the urinary system",
        "optC": "the immune defences", "optD": "the neural system"},
    "arcc_test_0316": {
        "prompt": "Each of these is a safe practice in the laboratory except",
        "optA": "keeping the bench tidy.",
        "optB": "putting on protective goggles while working.",
        "optC": "combining chemicals before the instructions have been read.",
        "optD": "scrubbing the hands well once the work is finished."},
    "arcc_test_0319": {
        "prompt": "Which of these will hold on to the greatest amount of the Sun's energy?",
        "optA": "ice crystals on the ground", "optB": "grains on a beach",
        "optC": "a lawn", "optD": "a pond"},
    "arcc_test_0329": {
        "prompt": "Irene wants to join two boards together. Which of these would NOT be "
                  "used to join them?",
        "optA": "adhesive", "optB": "threaded fasteners",
        "optC": "hammered pins", "optD": "a cutting blade"},
    "arcc_test_0354": {
        "prompt": "One property belongs to water alone. Which is it?",
        "optA": "It has a small heat capacity.",
        "optB": "It can be turned from liquid into solid.",
        "optC": "It takes very few substances into solution.",
        "optD": "It is found on Earth in all three states without help."},
    "arcc_test_0380": {
        "prompt": "Which of these is a case of current flowing in a circuit to make sound?",
        "optA": "pressing a button so a doorbell rings",
        "optB": "treading on a mat so a door opens",
        "optC": "throwing a switch so a lamp lights",
        "optD": "sliding a lever so an electric blanket warms"},
    "arcc_test_0417": {
        "prompt": "Which of these objects would be described as translucent?",
        "optA": "a pupil's exercise book", "optB": "the looking glass on the bus",
        "optC": "the school's brick wall", "optD": "the lenses in a pupil's sunglasses"},
    "arcc_test_0419": {
        "prompt": "A student wants to find which hand soap kills more bacteria. Her "
                  "teacher tells her to vary only the soap and to keep the bacterium the "
                  "same. Testing one variable at a time is done because it",
        "optA": "makes the experiment finish sooner.",
        "optB": "makes the results more dependable.",
        "optC": "makes the graphs simpler to read.",
        "optD": "guarantees the students learn something."},
    "arcc_test_0443": {
        "prompt": "A science class is working on solutions. Which statement captures "
                  "what a solution is?",
        "optA": "It is a mixture that is the same all the way through.",
        "optB": "It is the liquid that a chemical reaction yields.",
        "optC": "It forms when two or more liquids are put together.",
        "optD": "It has two parts of unequal volume."},
    "arcc_test_0445": {
        "prompt": "In a forest ecosystem, what is the niche of a population of squirrels?",
        "optA": "to rot down remains", "optB": "to pollinate blossoms",
        "optC": "to return nutrients to the soil",
        "optD": "to gather acorns and hide them underground"},
    "arcc_test_0462": {
        "prompt": "Early Egyptians pictured the solar system as a rectangular box. Early "
                  "Greeks imagined a set of crystal-like spheres. Later it was seen as "
                  "planets orbiting the Sun. Why has the picture changed over the centuries?",
        "optA": "Scientists liked the newer models better.",
        "optB": "Fresh findings forced revisions.",
        "optC": "The newer models were simpler to sketch.",
        "optD": "The information was at last written into books."},
    "arcc_test_0471": {
        "prompt": "In what way does the skin help the body keep its internal balance?",
        "optA": "The skin carries oxygen about.",
        "optB": "The skin breaks viruses down.",
        "optC": "The skin passes signals to the brain.",
        "optD": "The skin holds temperature steady."},
    "arcc_test_0514": {
        "prompt": "Fossilised coral reefs found on land are evidence that",
        "optA": "salty water turns coral into fossils.",
        "optB": "the reefs grew in a lake of fresh water.",
        "optC": "the height of the ocean has shifted over the ages.",
        "optD": "coral reefs are able to grow on dry land."},
    "arcc_test_0515": {
        "prompt": "Sound travels faster through solids than through air because the "
                  "molecules in a solid are",
        "optA": "packed more tightly than those in air.",
        "optB": "shifted more easily than those in air.",
        "optC": "travelling faster than those in air.",
        "optD": "bigger than those in air."},
    "arcc_test_0516": {
        "prompt": "A scientist labels some amino acids with a special chemical marker and "
                  "follows it until it forms part of a large molecule in a cell. Where "
                  "does the marker turn up?",
        "optA": "a lipid molecule inside a membrane",
        "optB": "an enzyme molecule inside a lysosome",
        "optC": "a polysaccharide inside a cell wall",
        "optD": "a DNA molecule inside a mitochondrion"},
    "arcc_test_0523": {
        "prompt": "Scientists found that although infectious bacteria may become immune "
                  "to antibiotic drugs, some bacteria cannot withstand certain peptides, "
                  "which act as natural antibiotics inside the human body. Which new "
                  "technology grew out of that finding?",
        "optA": "man-made compounds that copy human peptides",
        "optB": "antibiotics taken in through the skin",
        "optC": "bacteria that attack organisms resistant to antibiotics",
        "optD": "antibiotics that adjust when bacteria become immune"},
}

# Options that cannot be reworded without naming a different thing: chemical
# equations, element and base names, periodic-table group labels, and the four
# states of matter. Same basis as Amendment 1 to Study 4; the stem is rewritten
# and the options are left alone.
EXEMPT = {
    "arcc_test_0082": "When a 25 g sample of water sits at -5°C, that water is",
    "arcc_test_0131": "Which of these sets lists metals only?",
    "arcc_test_0150": "A fertilizer is advertised as holding every chemical a plant needs "
                      "to grow quickly. It follows that the fertilizer contains all of "
                      "these except",
    "arcc_test_0156": "In DNA, which base pairs with cytosine?",
    "arcc_test_0291": "Which of these chemical equations is written correctly and shows "
                      "mass being conserved?",
    "arcc_test_0358": "Which group of the periodic table holds the elements that react "
                      "least readily?",
}
