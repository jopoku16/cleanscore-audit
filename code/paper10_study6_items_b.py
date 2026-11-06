"""Deep paraphrases for the remaining 37 control parents, written under rules 1-6.

Same rules as paper10_study6_items_a.py. Where a term has no synonym that names
the same thing, the item is exempt rather than forced: "lightning" cannot be
reworded, and neither can a compass bearing or a colour name.
"""

ITEMS = {
    "arcc_test_0577": {
        "prompt": "The Florida Fish and Wildlife Conservation Commission (FWC) has helped "
                  "build more than 300 artificial reefs in the Atlantic Ocean and the Gulf "
                  "of Mexico. Which is an unforeseen harmful outcome of putting these "
                  "reefs in place?",
        "optA": "It improved chances for recreation and diving.",
        "optB": "It improved the study of corals and other organisms.",
        "optC": "It drove up over-fishing and wrecked ecosystems.",
        "optD": "It raised the number of fish and other water-dwelling organisms."},
    "arcc_test_0595": {
        "prompt": "Cities limit how much pollution cars may give off. How does this most "
                  "likely benefit people?",
        "optA": "The air stays purer.", "optB": "Cars can go at higher speeds.",
        "optC": "Drivers become more skilful.",
        "optD": "Driving on the roads grows safer."},
    "arcc_test_0620": {
        "prompt": "Which of these has the greatest effect on how fast the wind blows?",
        "optA": "rainfall and snowfall", "optB": "the extent of cloud",
        "optC": "the wind's bearing", "optD": "atmospheric pressure"},
    "arcc_test_0627": {
        "prompt": "What can give an offspring a physical trait that neither parent shows?",
        "optA": "a mutation in a body cell of a parent",
        "optB": "a mutation in a sex cell of a parent",
        "optC": "a trait picked out by natural selection",
        "optD": "a trait picked out by breeders"},
    "arcc_test_0636": {
        "prompt": "Estuaries are changeable ecosystems where salt water and fresh water "
                  "mix, usually where a river runs down to an ocean. When would the salt "
                  "concentration in the estuary near the river's mouth be LOWEST?",
        "optA": "when the river runs low and the tide is out",
        "optB": "when the river runs high and the tide is out",
        "optC": "when the river runs low and the tide is in",
        "optD": "when the river runs high and the tide is in"},
    "arcc_test_0652": {
        "prompt": "Some plants grow where many animals eat leaves. Which feature would "
                  "best help those plants survive?",
        "optA": "sizeable fruits", "optB": "lengthy stems",
        "optC": "sharp spines", "optD": "brightly coloured blooms"},
    "arcc_test_0656": {
        "prompt": "A truck's suspension system takes in which parts?",
        "optA": "the motor and carburetor", "optB": "the axle shafts and the wheels they carry",
        "optC": "the brake units and silencer",
        "optD": "the steering column and speed gauge"},
    "arcc_test_0663": {
        "prompt": "Walking to school one morning a student notices the grass is wet while "
                  "the streets are dry. Which process most likely wetted the grass?",
        "optA": "condensing of vapour", "optB": "eroding of surfaces",
        "optC": "vaporising", "optD": "precipitating from cloud"},
    "arcc_test_0664": {
        "prompt": "Sunlight warms the air near the ground. What happens next?",
        "optA": "The warm air gives off radiation and cools again.",
        "optB": "The warm air turns to vapour in the cooler air.",
        "optC": "The warm air swells and lifts, setting up convection.",
        "optD": "The warm air can no longer hold water and drops it as rain."},
    "arcc_test_0722": {
        "prompt": "A container of liquid water stood outside during the day at 3°C. "
                  "Overnight the outside temperature fell to -2°C. That change most likely "
                  "made the water",
        "optA": "turn to droplets", "optB": "turn to vapour",
        "optC": "stay liquid", "optD": "turn solid"},
    "arcc_test_0766": {
        "prompt": "A scientist finds that a certain substance will help in treating nerve "
                  "damage. What is the best way for her to make the result known to other "
                  "scientists?",
        "optA": "She can telephone other scientists working on nerves.",
        "optB": "She can write to hospitals that treat nerve damage.",
        "optC": "She can post her conclusions on a website about the nervous system.",
        "optD": "She can publish her findings in a scientific journal dealing with nerves."},
    "arcc_test_0774": {
        "prompt": "Some chemical reactions take energy in and others give energy out. Of "
                  "the reactions in burning coal and in exploding fireworks, which gives "
                  "energy out?",
        "optA": "only the burning coal", "optB": "only the exploding fireworks",
        "optC": "the burning coal and the exploding fireworks alike",
        "optD": "neither the burning coal nor the exploding fireworks"},
    "arcc_test_0790": {
        "prompt": "Why is a sperm cell built so differently from an egg cell?",
        "optA": "A sperm cell has to travel to reach the egg cell.",
        "optB": "An egg cell has to split into many separate sperm cells.",
        "optC": "An egg cell has to travel to reach the sperm cell.",
        "optD": "A sperm cell has to join with many different egg cells."},
    "arcc_test_0824": {
        "prompt": "Two forces push on a wood block in opposite directions. What follows if "
                  "the forces are unbalanced?",
        "optA": "The block will even out the forces.",
        "optB": "The forces will turn back on themselves.",
        "optC": "The block's mass will alter.",
        "optD": "The block's place will alter."},
    "arcc_test_0851": {
        "prompt": "Few flowers grow on the northern arctic tundra, and those that do have "
                  "very short stems. How does that adaptation help them survive the arctic "
                  "climate?",
        "optA": "It keeps them from freezing.",
        "optB": "It stops consumers eating them.",
        "optC": "It keeps them from snapping in strong winds.",
        "optD": "It makes them very hard to pull out of the ground."},
    "arcc_test_0873": {
        "prompt": "A mouse is put at one end of a cardboard maze with cheese at the far "
                  "end. It smells the cheese and works out how to reach it. The mouse is using",
        "optA": "an acquired trait to gain an inherited one.",
        "optB": "an inherited trait to gain an acquired one.",
        "optC": "an acquired trait to gain a further acquired one.",
        "optD": "an inherited trait to gain a further inherited one."},
    "arcc_test_0880": {
        "prompt": "In the middle of a lab session someone knocks a beaker and its "
                  "contents run across the bench. What is the first thing to do?",
        "optA": "tell the teacher", "optB": "mop up the spill",
        "optC": "tell someone in the class", "optD": "call the caretaker"},
    "arcc_test_0921": {
        "prompt": "Some fish on sale in grocery stores are raised on fish farms. As more "
                  "fish farms are built, which group is most likely to lose out?",
        "optA": "those who own grocery stores",
        "optB": "the drivers who haul the fish",
        "optC": "those who sell fish caught in the wild",
        "optD": "the builders who put the farms up"},
    "arcc_test_0935": {
        "prompt": "Where two continental plates run into each other, which geological "
                  "feature most often forms?",
        "optA": "a sea basin", "optB": "an erupting peak",
        "optC": "a river-cut valley", "optD": "a range of mountains"},
    "arcc_test_0941": {
        "prompt": "In the solid phase, water takes a crystal structure that holds its "
                  "molecules farther apart than they sit in the liquid phase at some "
                  "temperatures. Which property does that explain?",
        "optA": "that ice holds more impurities than liquid water",
        "optB": "that ice is able to float on liquid water",
        "optC": "that heat is given off when liquid water freezes into ice",
        "optD": "that liquid water cools as it runs over ice"},
    "arcc_test_0952": {
        "prompt": "Many grass snakes are green. That colour most likely helps the snake to",
        "optA": "climb high trees.", "optB": "squeeze into narrow spaces.",
        "optC": "stay out of sight when in danger.", "optD": "cast off its skin."},
    "arcc_test_1015": {
        "prompt": "In what way do plant cells differ from animal cells?",
        "optA": "Growth happens only in plant cells.",
        "optB": "Reproduction happens only in animal cells.",
        "optC": "Only animal cells can hold energy in store.",
        "optD": "Only plant cells can carry out photosynthesis."},
    "arcc_test_1044": {
        "prompt": "Which of these is an example of a physical change rather than "
                  "a chemical one?",
        "optA": "wool being knitted into a jumper",
        "optB": "a tractor's engine being started",
        "optC": "rust forming on a bicycle's metal",
        "optD": "grass taking in the energy of sunlight"},
    "arcc_test_1045": {
        "prompt": "The Ring of Fire is a long chain of volcanoes around the Pacific Ocean. "
                  "What best explains how these volcanoes are laid out?",
        "optA": "They trace the rim of a crater left by an asteroid strike.",
        "optB": "They follow the outline of the neighbouring tectonic plates beneath the sea.",
        "optC": "One volcano generally sets off a second with its hot magma.",
        "optD": "Volcanoes always form rings because of convection currents underwater."},
    "arcc_test_1056": {
        "prompt": "Which kind of cell connects to muscle fibres so the muscle can be "
                  "controlled?",
        "optA": "neural", "optB": "bone-forming",
        "optC": "cardiovascular", "optD": "pulmonary"},
    "arcc_test_1070": {
        "prompt": "Temperatures along a coast usually swing less than temperatures well "
                  "inland. Which statement best explains that?",
        "optA": "The coast is far windier than places inland.",
        "optB": "The land's temperature stays fairly steady.",
        "optC": "The coast is far drier than places inland.",
        "optD": "The ocean's temperature stays fairly steady."},
    "arcc_test_1088": {
        "prompt": "Which of these is an environmental gain from switching to solar power?",
        "optA": "less pollution in the air", "optB": "a higher cost for energy",
        "optC": "greater use of fossil fuels", "optD": "less electrical energy produced"},
    "arcc_test_1111": {
        "prompt": "A group of students tested how different amounts of water affected the "
                  "growth of ivy plants. Afterwards they could not recall how much each "
                  "plant had grown each day. What should they have done to work "
                  "scientifically?",
        "optA": "Talk over what they saw with other groups in the class.",
        "optB": "Run the experiment on more than one kind of plant.",
        "optC": "Write the daily figures into a data table.",
        "optD": "Invent explanations for the results."},
    "arcc_test_1116": {
        "prompt": "Which tool would help most in an investigation of a monarch butterfly's "
                  "life cycle?",
        "optA": "a keen-edged knife", "optB": "a hand lens",
        "optC": "a long length of string",
        "optD": "a big jar with air holes punched in the lid"},
    "arcc_test_1122": {
        "prompt": "When newly found information backs an established theory in a fresh "
                  "way, the theory",
        "optA": "grows and shifts.", "optB": "no longer holds.",
        "optC": "turns into a law.", "optD": "loses its worth."},
    "arcc_test_1141": {
        "prompt": "Which human action helps keep a renewable resource going?",
        "optA": "putting up power stations fuelled by coal",
        "optB": "clearing ground for roads and buildings",
        "optC": "channelling fertilizer runoff into ponds",
        "optD": "planting trees again where forest was cleared"},
}

EXEMPT = {
    "arcc_test_0525": "Which of these does photosynthesis produce?",
    "arcc_test_0606": "A student shines a flashlight onto sheets of paper in different "
                      "colors. Which color takes in the most light?",
    "arcc_test_0848": "A meteor moving through Earth's atmosphere travels at 35 km/sec, "
                      "and friction with the atmosphere slows it by 0.02 km/sec before it "
                      "reaches the surface. What speed does the meteor end up with?",
    # "lightning" names one thing and has no synonym that names the same thing.
    "arcc_test_1013": "In the nitrogen cycle, nitrogen can pass straight from the "
                      "atmosphere back to the lithosphere by way of",
    # "ice" names one substance and any rewording of it names something else.
    "arcc_test_1071": "About 71 % of Earth's surface is covered by water, most of it "
                      "salt water in the oceans. Where is most of Earth's fresh water held?",
    "arcc_test_1023": "A battery-powered toy sailboat heading south across a pond meets a "
                      "wind blowing from the east toward the west. Which way will the "
                      "combined forces send the boat?",
}
