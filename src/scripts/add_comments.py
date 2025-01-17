import pandas

# Change this to match your file path
FILE_NAME = '../../data/feedback/gautam.csv'

FILE_COMMIT = '../../data/comment_set.tsv'

PROMPT_1 = "Write a letter to your local newspaper in which you state your opinion on the effects computers have on " \
           "people. Persuade the readers to agree with you."

PROMPT_2 = "Write a persuasive essay to a newspaper reflecting your views on censorship in libraries. Do you believe " \
           "that certain materials, such as books, music, movies, magazines, etc., should be removed from the " \
           "shelves if they are found offensive? Support your position with convincing arguments from your own " \
           "experience, observations, and/or reading."

PROMPT_3 = "Write a response that explains how the features of the setting affect the cyclist. In your response, " \
           "include examples from the essay that support your conclusion"

PROMPT_3_TEXT = "FORGET THAT OLD SAYING ABOUT NEVER taking candy from strangers. No, a better piece of advice for the" \
                " solo cyclist would be, “Never accept travel advice from a collection of old-timers who haven’t left" \
                " the confines of their porches since Carter was in office.” It’s not that a group of old guys " \
                "doesn’t know the terrain. With age comes wisdom and all that, but the world is a fluid place. " \
                "Things change. \nAt a reservoir campground outside of Lodi, California, I enjoyed the serenity of an" \
                " early-summer evening and some lively conversation with these old codgers. What I shouldn’t have " \
                "done was let them have a peek at my map. Like a foolish youth, the next morning I followed their " \
                "advice and launched out at first light along a “shortcut” that was to slice away hours from my ride " \
                "to Yosemite National Park. \nThey’d sounded so sure of themselves when pointing out landmarks and " \
                "spouting off towns I would come to along this breezy jaunt. Things began well enough. I rode into " \
                "the morning with strong legs and a smile on my face. About forty miles into the pedal, I arrived at " \
                "the first “town.” This place might have been a thriving little spot at one time—say, before the last" \
                " world war—but on that morning it fit the traditional definition of a ghost town. I chuckled, " \
                "checked my water supply, and moved on. The sun was beginning to beat down, but I barely noticed it. " \
                "The cool pines and rushing rivers of Yosemite had my name written all over them. \nTwenty miles up " \
                "the road, I came to a fork of sorts. One ramshackle shed, several rusty pumps, and a corral that " \
                "couldn’t hold in the lamest mule greeted me. This sight was troubling. I had been hitting my water " \
                "bottles pretty regularly, and I was traveling through the high deserts of California in June. \nI " \
                "got down on my hands and knees, working the handle of the rusted water pump with all my strength. " \
                "A tarlike substance oozed out, followed by brackish water feeling somewhere in the neighborhood of " \
                "two hundred degrees. I pumped that handle for several minutes, but the water wouldn’t cool down. It " \
                "didn’t matter. When I tried a drop or two, it had the flavor of battery acid. \nThe old guys had " \
                "sworn the next town was only eighteen miles down the road. I could make that! I would conserve my " \
                "water and go inward for an hour or so—a test of my inner spirit. \nNot two miles into this next " \
                "section of the ride, I noticed the terrain changing. Flat road was replaced by short, rolling " \
                "hills. After I had crested the first few of these, a large highway sign jumped out at me. It read: " \
                "ROUGH ROAD AHEAD: DO NOT EXCEED POSTED SPEED LIMIT. \nThe speed limit was 55 mph. I was doing a " \
                "water-depleting 12 mph. Sometimes life can feel so cruel. \nI toiled on. At some point, tumbleweeds " \
                "crossed my path and a ridiculously large snake—it really did look like a diamondback—blocked the " \
                "majority of the pavement in front of me. I eased past, trying to keep my balance in my dehydrated " \
                "state. \nThe water bottles contained only a few tantalizing sips. Wide rings of dried sweat circled " \
                "my shirt, and the growing realization that I could drop from heatstroke on a gorgeous day in June " \
                "simply because I listened to some gentlemen who hadn’t been off their porch in decades, caused me " \
                "to laugh. \nIt was a sad, hopeless laugh, mind you, but at least I still had the energy to feel " \
                "sorry for myself. There was no one in sight, not a building, car, or structure of any kind. I began " \
                "breaking the ride down into distances I could see on the horizon, telling myself that if I could " \
                "make it that far, I’d be fi ne. \nOver one long, crippling hill, a building came into view. I wiped " \
                "the sweat from my eyes to make sure it wasn’t a mirage, and tried not to get too excited. With what " \
                "I believed was my last burst of energy, I maneuvered down the hill. \nIn an ironic twist that should" \
                " please all sadists reading this, the building—abandoned years earlier, by the looks of it—had been " \
                "a Welch’s Grape Juice factory and bottling plant. A sandblasted picture of a young boy pouring a " \
                "refreshing glass of juice into his mouth could still be seen. \nI hung my head. \nThat smoky blues " \
                "tune “Summertime” rattled around in the dry honeycombs of my deteriorating brain. I got back on the" \
                " \nbike, but not before I gathered up a few pebbles and stuck them in my mouth. I’d read once that " \
                "sucking on stones helps take your mind off thirst by allowing what spit you have left to circulate. " \
                "With any luck I’d hit a bump and lodge one in my throat. \nIt didn’t really matter. I was going to " \
                "die and the birds would pick me clean, leaving only some expensive outdoor gear and a diary with the" \
                " last entry in praise of old men, their wisdom, and their keen sense of direction. I made a mental " \
                "note to change that paragraph if it looked like I was going to lose consciousness for the last time." \
                " \nSomehow, I climbed away from the abandoned factory of juices and dreams, slowly gaining elevation" \
                " while losing hope. Then, as easily as rounding a bend, my troubles, thirst, and fear were all " \
                "behind me. \nGARY AND WILBER’S FISH CAMP—IF YOU WANT BAIT FOR THE BIG ONES, WE’RE YOUR BEST BET! " \
                "\n“And the only bet,” I remember thinking. \nAs I stumbled into a rather modern bathroom and drank " \
                "deeply from the sink, I had an overwhelming urge to seek out Gary and Wilber, kiss them, and buy " \
                "some bait—any bait, even though I didn’t own a rod or reel. \nAn old guy sitting in a chair under " \
                "some shade nodded in my direction. Cool water dripped from my head as I slumped against the wall " \
                "beside him. \n“Where you headed in such a hurry?” \n“Yosemite,” I whispered. \n“Know the best way " \
                "to get there?” \nI watched him from the corner of my eye for a long moment. He was even older " \
                "than the group I’d listened to in Lodi. \n“Yes, sir! I own a very good map.” \nAnd I promised myself" \
                " right then that I’d always stick to it in the future."

PROMPT_4 = "Read the last paragraph of the story. \n\"When they come back, Saeng vowed silently to herself, in the " \
           "spring, when the snows melt and the geese return and this hibiscus is budding, then I will take that test" \
           " again.\" \nWrite a response that explains why the author concludes the story with this paragraph. In " \
           "your response, include details and examples from the story that support your ideas."

PROMPT_4_TEXT = "Saeng, a teenage girl, and her family have moved to the United States from Vietnam. As Saeng walks " \
                "home after failing her driver’s test, she sees a familiar plant. Later, she goes to a florist shop " \
                "to see if the plant can be purchased. It was like walking into another world. A hot, moist world " \
                "exploding with greenery. Huge flat leaves, delicate wisps of tendrils, ferns and fronds and vines " \
                "of all shades and shapes grew in seemingly random profusion. \n“Over there, in the corner, the " \
                "hibiscus. Is that what you mean?” The florist pointed at a leafy potted plant by the corner. " \
                "\nThere, in a shaft of the wan afternoon sunlight, was a single blood-red blossom, its five petals " \
                "splayed back to reveal a long stamen tipped with yellow pollen. Saeng felt a shock of recognition so" \
                " intense, it was almost visceral. \n“Saebba,” Saeng whispered. A saebba hedge, tall and lush, had " \
                "surrounded their garden, its lush green leaves dotted with vermilion flowers. And sometimes after a " \
                "monsoon rain, a blossom or two would have blown into the well, so that when she drew the well water," \
                " she would find a red blossom floating in the bucket. \nSlowly, Saeng walked down the narrow aisle " \
                "toward the hibiscus. Orchids, lanna bushes, oleanders, elephant ear begonias, and bougainvillea " \
                "vines surrounded her. Plants that she had not even realized she had known but had forgotten drew her" \
                " back into her childhood world. When she got to the hibiscus, she reached out and touched a petal " \
                "gently. It felt smooth and cool, with a hint of velvet toward the center—just as she had known it " \
                "would feel. \nAnd beside it was yet another old friend, a small shrub with waxy leaves and dainty " \
                "flowers with purplish petals and white centers. “Madagascar periwinkle,” its tag announced. How " \
                "strange to see it in a pot, Saeng thought. Back home it just grew wild, jutting out from the cracks " \
                "in brick walls or between tiled roofs. \nAnd that rich, sweet scent—that was familiar, too. Saeng " \
                "scanned the greenery around her and found a tall, gangly plant with exquisite little white blossoms " \
                "on it. “Dok Malik,” she said, savoring the feel of the word on her tongue, even as she silently " \
                "noted the English name on its tag, “jasmine.” \nOne of the blossoms had fallen off, and carefully " \
                "Saeng picked it up and smelled it. She closed her eyes and breathed in, deeply. The familiar " \
                "fragrance filled her lungs, and Saeng could almost feel the light strands of her grandmother’s long " \
                "gray hair, freshly washed, as she combed it out with the fine-toothed buffalo-horn comb. And when " \
                "the sun had dried it, Saeng would help the gnarled old fingers knot the hair into a bun, then slip " \
                "a dok Malik bud into it. \nSaeng looked at the white bud in her hand now, small and fragile. " \
                "Gently, she closed her palm around it and held it tight. That, at least, she could hold on to. But " \
                "where was the fine-toothed comb? The hibiscus hedge? The well? Her gentle grandmother? \nA wave of " \
                "loss so deep and strong that it stung Saeng’s eyes now swept over her. A blink, a channel switch, " \
                "a boat ride into the night, and it was all gone. Irretrievably, irrevocably gone. \nAnd in the warm " \
                "moist shelter of the greenhouse, Saeng broke down and wept. \nIt was already dusk when Saeng reached" \
                " home. The wind was blowing harder, tearing off the last remnants of green in the chicory weeds that" \
                " were growing out of the cracks in the sidewalk. As if oblivious to the cold, her mother was still " \
                "out in the vegetable garden, digging up the last of the onions with a rusty trowel. She did not see " \
                "Saeng until the girl had quietly knelt down next to her. \nHer smile of welcome warmed Saeng. “Ghup " \
                "ma laio le? You’re back?” she said cheerfully. “Goodness, it’s past five. What took you so long? " \
                "How did it go? Did you—?” Then she noticed the potted plant that Saeng was holding, its leaves " \
                "quivering in the wind. \nMrs. Panouvong uttered a small cry of surprise and delight. “Dok faeng-noi!" \
                "” she said. “Where did you get it?” \n“I bought it,” Saeng answered, dreading her mother’s next " \
                "question. \n“How much?” \nFor answer Saeng handed her mother some coins. \n“That’s all?” " \
                "Mrs. Panouvong said, appalled, “Oh, but I forgot! You and the \nLambert boy ate Bee-Maags....” " \
                "\n“No, we didn’t, Mother,” Saeng said. \n“Then what else—?” \n“Nothing else. I paid over nineteen " \
                "dollars for it.” \n“You what?” Her mother stared at her incredulously. “But how could you? All the " \
                "seeds for this vegetable garden didn’t cost that much! You know how much we—” She paused, as she " \
                "noticed the tearstains on her daughter’s cheeks and her puffy eyes. \n“What happened?” she asked, " \
                "more gently. \n“I—I failed the test,” Saeng said. \nFor a long moment Mrs. Panouvong said nothing. " \
                "Saeng did not dare look her mother in the eye. Instead, she stared at the hibiscus plant and " \
                "nervously tore off a leaf, shredding it to bits. \nHer mother reached out and brushed the fragments " \
                "of green off Saeng’s hands. “It’s a beautiful plant, this dok faeng-noi,” she finally said. “I’m " \
                "glad you got it.” \n“It’s—it’s not a real one,” Saeng mumbled. \n“I mean, not like the kind we had " \
                "at—at—” She found that she was still too shaky to say the words at home, lest she burst into tears " \
                "again. “Not like the kind we had before,” she said. \n“I know,” her mother said quietly. “I’ve seen " \
                "this kind blooming along the lake. Its flowers aren’t as pretty, but it’s strong enough to make it " \
                "through the cold months here, this winter hibiscus. That’s what matters.” \nShe tipped the pot and " \
                "deftly eased the ball of soil out, balancing the rest of the plant in her other hand. “Look how " \
                "root-bound it is, poor thing,” she said. “Let’s plant it, right now.” \nShe went over to the corner " \
                "of the vegetable patch and started to dig a hole in the ground. The soil was cold and hard, and she " \
                "had trouble thrusting the shovel into it. Wisps of her gray hair trailed out in the breeze, and her " \
                "slight frown deepened the wrinkles around her eyes. There was a frail, wiry beauty to her that " \
                "touched Saeng deeply. \n“Here, let me help, Mother,” she offered, getting up and taking the shovel " \
                "away from her. \nMrs. Panouvong made no resistance. “I’ll bring in the hot peppers and bitter " \
                "melons, then, and start dinner. How would you like an omelet with slices of the bitter melon?” " \
                "\n“I’d love it,” Saeng said. \nLeft alone in the garden, Saeng dug out a hole and carefully lowered " \
                "the “winter hibiscus” into it. She could hear the sounds of cooking from the kitchen now, the " \
                "beating of eggs against a bowl, the sizzle of hot oil in the pan. The pungent smell of bitter melon " \
                "wafted out, and Saeng’s mouth watered. It was a cultivated taste, she had discovered—none of her " \
                "classmates or friends, not even Mrs. Lambert, liked it—this sharp, bitter melon that left a golden " \
                "aftertaste on the tongue. But she had grown up eating it and, she admitted to herself, much " \
                "preferred it to a Big Mac. \nThe “winter hibiscus” was in the ground now, and Saeng tamped down the " \
                "soil around it. Overhead, a flock of Canada geese flew by, their faint honks clear and—yes—familiar " \
                "to Saeng now. Almost reluctantly, she realized that many of the things that she had thought of as " \
                "strange before had become, through the quiet repetition of season upon season, almost familiar to " \
                "her now. Like the geese. She lifted her head and watched as their distinctive V was etched against " \
                "the evening sky, slowly fading into the distance. \nWhen they come back, Saeng vowed silently to " \
                "herself, in the spring, when the snows melt and the geese return and this hibiscus is budding, then " \
                "I will take that test again."

PROMPT_5 = "Describe the mood created by the author in the memoir. Support your answer with relevant and specific " \
           "information from the memoir."

PROMPT_5_TEXT = "My parents, originally from Cuba, arrived in the United States in 1956. After living for a year in " \
                "a furnished one-room apartment, twenty-one-year-old Rawedia Maria and twenty-seven-year-old Narciso " \
                "Rodriguez, Sr., could afford to move into a modest, three-room apartment I would soon call home. " \
                "\nIn 1961, I was born into this simple house, situated in a two-family, blond-brick building in the " \
                "Ironbound section of Newark, New Jersey. Within its walls, my young parents created our traditional " \
                "Cuban home, the very heart of which was the kitchen. My parents both shared cooking duties and " \
                "unwittingly passed on to me their rich culinary skills and a love of cooking that is still with me " \
                "today (and for which I am eternally grateful). Passionate Cuban music (which I adore to this day) " \
                "filled the air, mixing with the aromas of the kitchen. Here, the innocence of childhood, the " \
                "congregation of family and friends, and endless celebrations that encompassed both, formed the " \
                "backdrop to life in our warm home. \nGrowing up in this environment instilled in me a great sense " \
                "that “family” had nothing to do with being a blood relative. Quite the contrary, our neighborhood " \
                "was made up of mostly Spanish, Cuban, and Italian immigrants at a time when overt racism was the " \
                "norm and segregation prevailed in the United States. In our neighborhood, despite customs elsewhere," \
                " all of these cultures came together in great solidarity and friendship. It was a close-knit " \
                "community of honest, hardworking immigrants who extended a hand to people who, while not necessarily" \
                " their own kind, were clearly in need. \nOur landlord and his daughter, Alegria (my babysitter and " \
                "first friend), lived above us, and Alegria graced our kitchen table for meals more often than not. " \
                "Also at the table were Sergio and Edelmira, my surrogate grandparents who lived in the basement " \
                "apartment. (I would not know my “real” grandparents, Narciso the Elder and Consuelo, until 1970 when" \
                " they were allowed to leave Cuba.) My aunts Bertha and Juanita and my cousins Arnold, Maria, and " \
                "Rosemary also all lived nearby and regularly joined us at our table. Countless extended family " \
                "members came and went — and there was often someone staying with us temporarily until they were able" \
                " to get back on their feet. My parents always kept their arms and their door open to the many people" \
                " we considered family, knowing that they would do the same for us. \nMy mother and father had come " \
                "to this country with such courage, without any knowledge of the language or the culture. They came " \
                "selflessly, as many immigrants do, to give their children a better life, even though it meant " \
                "leaving behind their families, friends, and careers in the country they loved. They struggled both " \
                "personally and financially, braving the harsh northern winters while yearning for their native " \
                "tropics and facing cultural hardships. The barriers to work were strong and high, and my parents " \
                "both had to accept that they might not be able to find the kind of jobs they deserved. In Cuba, " \
                "Narciso, Sr., had worked in a laboratory and Rawedia Maria had studied chemical engineering. In the " \
                "United States, they had to start their lives over entirely, taking whatever work they could find. " \
                "The faith that this struggle would lead them and their children to better times drove them to endure" \
                " these hard times. \nI will always be grateful to my parents for their love and sacrifice. I’ve " \
                "often told them that what they did was a much more courageous thing than I could have ever done. " \
                "I’ve often told them of my admiration for their strength and perseverance, and I’ve thanked them " \
                "repeatedly. But, in reality, there is no way to express my gratitude for the spirit of generosity " \
                "impressed upon me at such an early age and the demonstration of how important family and friends are" \
                ". These are two lessons that my parents did not just tell me. They showed me with their lives, and " \
                "these teachings have been the basis of my life. \nIt was in this simple house that my parents " \
                "welcomed other refugees to celebrate their arrival to this country and where I celebrated my first " \
                "birthdays. It was in the warmth of the kitchen in this humble house where a Cuban feast (albeit a " \
                "frugal Cuban feast) always filled the air with not just scent and music but life and love. It was " \
                "here where I learned the real definition of “family.” And for this, I will never forget that house " \
                "or its gracious neighborhood or the many things I learned there about how to love. I will never " \
                "forget how my parents turned this simple house into a home."

PROMPT_6 = "Based on the excerpt, describe the obstacles the builders of the Empire State Building faced in " \
           "attempting to allow dirigibles to dock there. Support your answer with relevant and specific information " \
           "from the excerpt."

PROMPT_6_TEXT = "When the Empire State Building was conceived, it was planned as the world’s tallest building, taller" \
                " even than the new Chrysler Building that was being constructed at Forty-second Street and " \
                "Lexington Avenue in New York. At seventy-seven stories, it was the tallest building before the " \
                "Empire State began construction, and Al Smith was determined to outstrip it in height. \nThe " \
                "architect building the Chrysler Building, however, had a trick up his sleeve. He secretly " \
                "constructed a 185-foot spire inside the building, and then shocked the public and the media by " \
                "hoisting it up to the top of the Chrysler Building, bringing it to a height of 1,046 feet, 46 feet " \
                "taller than the originally announced height of the Empire State Building. \nAl Smith realized that " \
                "he was close to losing the title of world’s tallest building, and on December 11, 1929, he announced" \
                " that the Empire State would now reach the height of 1,250 feet. He would add a top or a hat to the " \
                "building that would be even more distinctive than any other building in the city. John Tauranac " \
                "describes the plan: \n[The top of the Empire State Building] would be more than ornamental, more " \
                "than a spire or dome or a pyramid put there to add a desired few feet to the height of the building " \
                "or to mask something as mundane as a water tank. Their top, they said, would serve a higher calling." \
                " The Empire State Building would be equipped for an age of transportation that was then only the " \
                "dream of aviation pioneers. \nThis dream of the aviation pioneers was travel by dirigible, or " \
                "zeppelin, and the Empire State Building was going to have a mooring mast at its top for docking " \
                "these new airships, which would accommodate passengers on already existing transatlantic routes and " \
                "new routes that were yet to come. \n\nThe Age of Dirigibles \nBy the 1920s, dirigibles were being " \
                "hailed as the transportation of the future. Also known today as blimps, dirigibles were actually " \
                "enormous steel-framed balloons, with envelopes of cotton fabric filled with hydrogen and helium to " \
                "make them lighter than air. Unlike a balloon, a dirigible could be maneuvered by the use of " \
                "propellers and rudders, and passengers could ride in the gondola, or enclosed compartment, under " \
                "the balloon. \nDirigibles had a top speed of eighty miles per hour, and they could cruise at " \
                "seventy miles per hour for thousands of miles without needing refueling. Some were as long as one " \
                "thousand feet, the same length as four blocks in New York City. The one obstacle to their expanded " \
                "use in New York City was the lack of a suitable landing area. Al Smith saw an opportunity for his " \
                "Empire State Building: A mooring mast added to the top of the building would allow dirigibles to " \
                "anchor there for several hours for refueling or service, and to let passengers off and on. " \
                "Dirigibles were docked by means of an electric winch, which hauled in a line from the front of the " \
                "ship and then tied it to a mast. The body of the dirigible could swing in the breeze, and yet " \
                "passengers could safely get on and off the dirigible by walking down a gangplank to an open " \
                "observation platform. \nThe architects and engineers of the Empire State Building consulted " \
                "with experts, taking tours of the equipment and mooring operations at the U.S. Naval Air Station " \
                "in Lakehurst, New Jersey. The navy was the leader in the research and development of dirigibles in " \
                "the United States. The navy even offered its dirigible, the Los Angeles, to be used in testing the " \
                "mast. The architects also met with the president of a recently formed airship transport company " \
                "that planned to offer dirigible service across the Pacific Ocean. \nWhen asked about the mooring " \
                "mast, Al Smith commented: [It’s] on the level, all right. No kidding. We’re working on the thing " \
                "now. One set of engineers here in New York is trying to dope out a practical, workable arrangement " \
                "and the Government people in Washington are figuring on some safe way of mooring airships to this " \
                "mast. \n\nDesigning the Mast \nThe architects could not simply drop a mooring mast on top of the " \
                "Empire State Building’s flat roof. A thousand-foot dirigible moored at the top of the building, " \
                "held by a single cable tether, would add stress to the building’s frame. The stress of the " \
                "dirigible’s load and the wind pressure would have to be transmitted all the way to the building’s " \
                "foundation, which was nearly eleven hundred feet below. The steel frame of the Empire State Building" \
                " would have to be modified and strengthened to accommodate this new situation. Over sixty thousand " \
                "dollars’ worth of modifications had to be made to the building’s framework. \nRather than building " \
                "a utilitarian mast without any ornamentation, the architects designed a shiny glass and " \
                "chrome-nickel stainless steel tower that would be illuminated from inside, with a stepped-back " \
                "design that imitated the overall shape of the building itself. The rocket-shaped mast would have " \
                "four wings at its corners, of shiny aluminum, and would rise to a conical roof that would house the " \
                "mooring arm. The winches and control machinery for the dirigible mooring would be housed in the base" \
                " of the shaft itself, which also housed elevators and stairs to bring passengers down to the " \
                "eighty-sixth floor, where baggage and ticket areas would be located. \nThe building would now be " \
                "102 floors, with a glassed-in observation area on the 101st floor and an open observation platform " \
                "on the 102nd floor. This observation area was to double as the boarding area for dirigible " \
                "passengers. \nOnce the architects had designed the mooring mast and made changes to the existing " \
                "plans for the building’s skeleton, construction proceeded as planned. When the building had been " \
                "framed to the 85th floor, the roof had to be completed before the framing for the mooring mast could" \
                " take place. The mast also had a skeleton of steel and was clad in stainless steel with glass " \
                "windows. Two months after the workers celebrated framing the entire building, they were back to " \
                "raise an American flag again—this time at the top of the frame for the mooring mast. \n\nThe Fate of" \
                " the Mast \nThe mooring mast of the Empire State Building was destined to never fulfill its purpose," \
                " for reasons that should have been apparent before it was ever constructed. The greatest reason was " \
                "one of safety: Most dirigibles from outside of the United States used hydrogen rather than helium, " \
                "and hydrogen is highly flammable. When the German dirigible Hindenburg was destroyed by fire in " \
                "Lakehurst, New Jersey, on May 6, 1937, the owners of the Empire State Building realized how much " \
                "worse that accident could have been if it had taken place above a densely populated area such as " \
                "downtown New York. \nThe greatest obstacle to the successful use of the mooring mast was nature " \
                "itself. The winds on top of the building were constantly shifting due to violent air currents. Even " \
                "if the dirigible were tethered to the mooring mast, the back of the ship would swivel around and " \
                "around the mooring mast. Dirigibles moored in open landing fields could be weighted down in the " \
                "back with lead weights, but using these at the Empire State Building, where they would be dangling " \
                "high above pedestrians on the street, was neither practical nor safe. \nThe other practical reason " \
                "why dirigibles could not moor at the Empire State Building was an existing law against airships " \
                "flying too low over urban areas. This law would make it illegal for a ship to ever tie up to the " \
                "building or even approach the area, although two dirigibles did attempt to reach the building " \
                "before the entire idea was dropped. In December 1930, the U.S. Navy dirigible Los Angeles " \
                "approached the mooring mast but could not get close enough to tie up because of forceful winds. " \
                "Fearing that the wind would blow the dirigible onto the sharp spires of other buildings in the area," \
                " which would puncture the dirigible’s shell, the captain could not even take his hands off the " \
                "control levers. \nTwo weeks later, another dirigible, the Goodyear blimp Columbia, attempted a " \
                "publicity stunt where it would tie up and deliver a bundle of newspapers to the Empire State " \
                "Building. Because the complete dirigible mooring equipment had never been installed, a worker atop " \
                "the mooring mast would have to catch the bundle of papers on a rope dangling from the blimp. The " \
                "papers were delivered in this fashion, but after this stunt the idea of using the mooring mast was " \
                "shelved. In February 1931, Irving Clavan of the building’s architectural office said, “The as yet " \
                "unsolved problems of mooring air ships to a fixed mast at such a height made it desirable to " \
                "postpone to a later date the final installation of the landing gear.” \nBy the late 1930s, the idea " \
                "of using the mooring mast for dirigibles and their passengers had quietly disappeared. Dirigibles, " \
                "instead of becoming the transportation of the future, had given way to airplanes. The rooms in the " \
                "Empire State Building that had been set aside for the ticketing and baggage of dirigible passengers " \
                "were made over into the world’s highest soda fountain and tea garden for use by the sightseers who " \
                "flocked to the observation decks. The highest open observation deck, intended for disembarking " \
                "passengers, has never been open to the public."

PROMPT_7 = "Write about patience. Being patient means that you are understanding and tolerant. A patient person " \
           "experience difficulties without complaining. \nDo only one of the following: write a story about a time " \
           "when you were patient OR write a story about a time when someone you know was patient OR write a story in" \
           " your own way about patience."

PROMPT_8 = "We all understand the benefits of laughter. For example, someone once said, “Laughter is the shortest " \
           "distance between two people.” Many other people believe that laughter is an important part of any " \
           "relationship. Tell a true story in which laughter was one element or part."

def main():
    stuff = pandas.read_csv(FILE_NAME, sep=',', encoding='ISO-8859-1')
    stuff = stuff.copy()

    if 'comments' not in stuff.keys():
        stuff['comments'] = None
        
    while True:
        num = input("\nYou can enter an essay id, [0] to save & exit, [TD] for essays to do, [P-(essay_set)] for each essay"
                    " prompt, or [T-(essay_set)] if the essay prompt has an associated text. If you use the [commit] "
                    "command, it will copy your work to the aggregate comment file, comment_set.csv : ")
        num = num.lower()
        if num == '0':
            break
        if num == 'td':
            print(stuff.loc[stuff['comments'].isnull()]['essay_id'].values)
            continue
        if num == 'commit':
            print("Copying data to ", FILE_COMMIT)
            dataset = pandas.read_csv(FILE_COMMIT, sep='\t', encoding='ISO-8859-1')
            dataset = dataset.copy()

            for i in range(len(stuff)):
                j = stuff.loc[i]
                if j['comments'] is None:
                    continue
                if dataset.loc[dataset['essay_id'] == j['essay_id']].empty:
                    dataset = dataset.append(j)
                else:
                    dataset.loc[dataset['essay_id'] == j['essay_id'], 'comments'] = j['comments']
            dataset.to_csv(FILE_COMMIT, sep='\t', index=False, encoding='ISO-8859-1')
            break
        if num == 'correct':
            for i in range(len(stuff)):
                text = stuff.loc[i]['comments'].split(",")
                if text[0] == 'ID1':
                    text[0] = 'ID3'
                else:
                    if text[0] == 'ID3':
                        text[0] = 'ID1'
                if text[1] == 'ORG1':
                    text[1] = 'ORG3'
                else:
                    if text[1] == 'ORG3':
                        text[1] = 'ORG1'
                if text[2] == 'STY1':
                    text[2] = 'STY3'
                else:
                    if text[2] == 'STY3':
                        text[2] = 'STY1'
                done = text[0] + "," + text[1] + "," + text[2]

                stuff.loc[i, 'comments'] = done
            stuff.to_csv(FILE_NAME, sep=',', index=False, encoding='ISO-8859-1')

        if len(num) == 3 and num[0:2] == 'p-' and 0 < int(num[2]) < 9:
            i = int(num[2])
            if i == 1:
                print(PROMPT_1)
            if i == 2:
                print(PROMPT_2)
            if i == 3:
                print(PROMPT_3)
            if i == 4:
                print(PROMPT_4)
            if i == 5:
                print(PROMPT_5)
            if i == 6:
                print(PROMPT_6)
            if i == 7:
                print(PROMPT_7)
            if i == 8:
                print(PROMPT_8)
            continue
        if len(num) == 3 and num[0:2] == 't-' and 2 < int(num[2]) < 7:
            i = int(num[2])
            if i == 3:
                print(PROMPT_3_TEXT)
            if i == 4:
                print(PROMPT_4_TEXT)
            if i == 5:
                print(PROMPT_5_TEXT)
            if i == 6:
                print(PROMPT_6_TEXT)
            continue

        if not num.isdigit():
            continue

        view = stuff.loc[stuff['essay_id'] == int(num)]

        if not view['essay'].values.size > 0:
            print("Enter a valid essay number")
            continue

        print("Essay Set: ", view['essay_set'].values)
        print(view['essay'].values)

        a = input("Enter the idea score(1-3): ")
        if a == '0' or not a.isdigit():
            break
        if not 0 < int(a) < 4:
            continue

        b = input("Enter the organization score(1-3): ")
        if b == '0' or not b.isdigit():
            break
        if not 0 < int(b) < 4:
            continue

        c = input("Enter the style score(1-3): ")
        if c == '0' or not c.isdigit():
            break
        if not 0 < int(c) < 4:
            continue
        stuff.loc[view.index.values[0], 'comments'] = "ID" + a + ",ORG" + b + ",STY" + c

    stuff.to_csv(FILE_NAME, sep=',', index=False, encoding='ISO-8859-1')

# This stops all the code from running when Sphinx imports the module.
if __name__ == '__main__':
    main()