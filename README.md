# Article:

## Check commits for more!
https://www.engadget.com/why-do-ai-data-centers-use-so-many-resources-171500010.html?src=rss

Why do AI data centers use so many resources?

The facilities supporting the AI boom present a novel strain of wastefulness.

Daniel Cooper, Cheyenne MacDonald

Fri, October 3, 2025 at 5:15 PM UTC

13 min read

OpenAI

With the AI boom, construction of new data centers has skyrocketed, and not without consequence — some communities that count these facilities as neighbors are now facing water shortages and strained power supplies. While tech's data center footprint has been growing for decades, generative AI has seemingly shifted the impacts of these operations toward the catastrophic. What exactly makes these new data centers such a burden on the environment and existing infrastructure, and is there anything we can do to fix it?

Chips

The industry believes AI will work its way into every corner of our lives, and so needs to build sufficient capacity to address that anticipated demand. But the hardware used to make AI work is so much more resource-intensive than standard cloud computing facilities that it requires a dramatic shift in how data centers are engineered.

Typically the most important part of a computer is its “brain,” the Central Processing Unit (CPU). It's designed to compute a wide variety of tasks, tackling them one at a time. Imagine a CPU as a one-lane motorway in which every vehicle, no matter the size, can get from A to B at extraordinary speed. What AI relies on instead are Graphics Processing Units (GPU), which are clusters of smaller, more specialized processors all running in parallel. In the example, a GPU is a thousand-lane motorway with a speed limit of just 30 mph. Both try to get a huge number of figurative vehicles to their destination in a short amount of time, but they take diametrically opposite approaches to solving that problem.

Advertisement

Advertisement

Phil Burr is Head of Product at Lumai, a British company looking to replace traditional GPUs with optical processors. “In AI, you repeatedly perform similar operations,” he explained, “and you can do that in parallel across the data set.” This gives GPUs an advantage over CPUs in large but fundamentally repetitive tasks, like graphics, executing AI models and crypto mining. “You can process a large amount of data very quickly, but its doing the same amount of processing each time,” he said.

In the same way that thousand-lane highway would be pretty wasteful, the more powerful GPUs get, the more energy hungry they become. “In the past, as [CPUs evolved] you could get a lot more transistors on a device, but the overall power [consumption] remained about the same," Burr said. They're also equipped with “specialized units that do [specific] work faster so the chip can return to idle sooner.” By comparison, “every iteration of a GPU has more and more transistors, but the power jumps up every time because getting gains from those processes is hard.” Not only are they physically larger — which results in higher power demands — but they “generally activate all of the processing units at once,” Burr said.

In 2024, the Lawrence Berkeley National Laboratory published a congressionally mandated report into the energy consumption of data centers. The report identified a sharp increase in the amount of electricity data centers consumed as GPUs became more prevalent. Power use from 2014 to 2016 was stable at around 60 TWh, but started climbing in 2018, to 76 TWh, and leaping to 176 TWh by 2023. In just five years, data center energy use more than doubled from 1.9 percent of the US total, to nearly 4.4 percent — with that figure projected to reach up to 12 percent by the start of the 2030s.

Heat

Like a lightbulb filament, as electricity moves through the silicon of computer chips, it encounters resistance, generating heat. Extending that power efficiency metaphor from earlier, CPUs are closer to modern LEDs here, while GPUs, like old incandescent bulbs, lose a huge amount of their power to resistance. The newest generation of AI data centers are filled with rack after rack of them, depending on the owners needs and budget, each one kicking out what Burr described as “a massive amount of heat.”

Advertisement

Advertisement

Heat isnt just an unwelcome byproduct: if chips arent kept cool, they'll experience performance and longevity issues. The American Society of Heating, Refrigerating and Air Conditioning Engineers (ASHRAE) publishes guidelines for data center operators. It advocates server rooms should be kept between 18 to 27 degrees celsius (64.4 to 80.6 degrees Fahrenheit). Given the sheer volume of heat GPUs kick out, maintaining that temperature requires some intensive engineering, and a lot of energy.

The majority of data centers use a handful of methods to keep their hardware within the optimal temperature. One of the oldest ways to maximize the efficiency of air conditioning is a technique of hot and cold aisle containment. Essentially, cold air is pushed through the server racks to keep them cool, while the hot air those servers expel is drawn out to be cooled and recirculated.

Many data centers, especially in the US, rely on the cooling effect that occurs as water changes from a liquid to a gas. This is done by drawing hot air through a wet medium to facilitate evaporation and blowing the resulting cooled air into the server room, in a method known as direct evaporative cooling. There's also indirect evaporative cooling, which works similarly but adds a heat exchanger — a device that's used to transfer heat between different mediums. In this type of setup, the heat from the warm air is transferred and cooled separately from the server room to avoid raising the humidity levels indoors.

Due in part to their cooling needs, data centers have a tremendous water footprint. The Lawrence Berkeley report found that, in 2014, US-based data centers consumed 21.2 billion liters of water. By 2018, however, that figure had leapt to 66 billion liters, much of which was attributed to what it collectively terms “hyperscale” facilities, which include AI-focused operations. In 2023, traditional US data centers reportedly consumed 10.56 billion liters of water while AI facilities used around 55.4 billion liters. The reports projections believe that by 2028, AI data centers will likely consume as much as 124 billion liters of water.

Advertisement

Advertisement

"Collectively, data centers are among the top-ten water consuming industrial or commercial industries in the US," according to a 2021 study published in the journal Environmental Research Letters. About one-fifth of these data centers use water from stressed watersheds, i.e. areas where the demand for water may be greater than the natural supply.

Most of the water consumed by data centers evaporates and won't be immediately replenished, while the rest goes to wastewater treatment plants. As a trio of academics explained in an op-ed for The Dallas Morning News, data centers are "effectively removing [drinking water] from the local water cycle." Water used in the cooling process is typically treated with chemicals such as corrosion inhibitors and biocides, which prevent bacterial growth. The resulting wastewater often contains pollutants, so it can't be recycled for human consumption or agriculture.

And data centers' water use goes well beyond cooling. A much bigger portion of their water footprint can be attributed to indirect uses, mainly through electricity generated by power plants but also through wastewater utilities. These account for about three-fourths of a data center's water footprint, the study notes. Power plants use water in a number of ways, primarily for cooling and to produce the steam needed to spin their electricity-generating turbines. According to the authors, 1 megawatt-hour of energy consumed by data centers in the US on average requires 7.1 cubic meters of water.

"Data centers are indirectly dependent on water from every state in the contiguous US, much of which is sourced from power plants drawing water from subbasins in the eastern and western coastal states," the authors explain. To adequately address the water issue, energy consumption must be reigned in too.

Exploring the alternatives

One major approach to reduce the massive water footprint of these systems is to use closed-loop liquid cooling. This is already ubiquitous on a smaller scale in high-end PCs, where heat-generating components, such as the CPU and GPU, have large heat exchangers that a liquid is pumped through. The liquid draws away the heat, and then has to be cooled down via another heat exchanger, or a refrigeration unit, before being recirculated.

Advertisement

Advertisement

Liquid cooling is becoming more and more common, especially in AI data centers, given the heat that GPUs generate. With the exception of mechanical issues, like leaking, and the water needed to operate the facility more generally, closed-loop systems do not experience water loss and so make more reasonable demands on local water resources. Direct-to-chip liquid cooling drastically cuts a data center's potential water use, and more efficiently removes heat than traditional air-cooling systems. In recent years, companies including Google, NVIDIA and Microsoft have been championing liquid cooling systems as a more sustainable way forward. And researchers are looking into ways to employ this approach on an even more granular level to tackle the heat right at the source.

Whereas cold plates (metal slabs with tubing or internal channels for coolant to flow through) are commonly used in liquid cooling systems to transfer heat away from the electronics, Microsoft has been testing a microfluidics-based cooling system in which liquid coolant travels through tiny channels on the back of the chip itself. In the lab, this system performed "up to three times better than cold plates at removing heat," and the company said it "can effectively cool a server running core services for a simulated Teams meeting." A blog post about the findings noted, "microfluidics also reduced the maximum temperature rise of the silicon inside a GPU by 65 percent, though this will vary by the type of chip."

Another option is "free" cooling, or making use of the natural environmental conditions at the data center site to cool the operation. Air-based free cooling utilizes the outdoor air in cold locales, while water-based free cooling relies on cold water sources such as seawater. Some facilities couple this with rainwater harvesting for their other water needs, like humidification.

A map of Start Campus

(Start Campus)

Start Campus, a data center project in Portugal, is located on the site of an old coal-fired power station and will use much of its old infrastructure. Rather than simply employ a closed-loop, the high temperatures will require the closed-loop system to interact with an open loop. When the campus is fully operational, its heat will be passed onto around 1.4 million cubic tons of seawater per day. Omer Wilson, CMO at Start Campus, said that by the time the water has returned to its source, its temperature will be the same as the surrounding sea. Start Campus has also pledged that there will be no meaningful water loss from this process.

Advertisement

Advertisement

There is another novel cooling method, immersion, in which computing equipment is — you guessed it — immersed in a non-conductive liquid suitable to draw heat. Wilson described it as a relatively niche approach, used in some crypto mining applications, but not used by industrial-scale facilities.

To keep with both energy and cooling needs, some researchers say the industry must look to renewable resources. "Directly connecting data center facilities to wind and solar energy sources ensures that water and carbon footprints are minimized," wrote the authors of the aforementioned Environmental Research study. Even purchasing renewable energy certificates — which each represent one megawatt-hour of electricity generated from a renewable source and delivered to the grid — could help shift the grid toward these sources over time, they added. "Data center workloads can be migrated between data centers to align with the portion of the grid where renewable electricity supplies exceed instantaneous demand."

Geothermal resources have begun to look especially promising. According to a recent report by the Rhodium Group, geothermal energy could meet up to 64 percent of data center's projected power demand growth in the US "by the early 2030s." In the Western US, geothermal could meet 100 percent of demand growth in areas such as Phoenix, Dallas-Fort Worth and Las Vegas.

For cooling, geothermal heat pumps can be used to "leverage the consistently cool temperatures" found hundreds of feet beneath the surface. Or, in locations where there are shallow aquifers present, data centers can make use of geothermal absorption chillers. These rely on the low-grade heat at shallower depths "to drive a chemical reaction that produces water vapor," the report explains. "This water vapor cools as it is run through a condenser and cools the IT components of a data center using evaporation."

Advertisement

Advertisement

Iron Mountain Data Centers operates a geothermally cooled data center in Boyers, Pennsylvania at the site of an old limestone mine. A 35-acre underground reservoir provides a year-round supply of cool water. Geothermal may not be a widespread solution just yet, but it's catching on. In 2024, Meta announced a partnership with Sage Geosystems to supply its data centers with up to 150 megawatts (MW) of geothermal power starting in 2027.

Beyond the hardware

While novel cooling methods will undoubtedly help curb some of the AI data centers' excessive resource demands, the first step to meaningful change is transparency, according to Vijay Gadepally, a senior scientist at MIT's Lincoln Laboratory Supercomputing Center. AI companies need to be upfront about the emissions and resource use associated with their operations to give people a clear view of their footprints.

Then there is the hardware to consider. Incorporating more intelligent chip design — i.e. processors with better performance characteristics — could go a long way toward making data centers more sustainable. "That's a huge area of innovation right now," Gadepally said. And large data centers are often "running underutilized," with a lot of power that isnt being allocated efficiently. Rather than leaning into the push to build more such facilities, the industry should first make better use of existing data centers' capacities.

Similarly, many of today's AI models are vastly overpowered for the tasks they're being given. The current approach is "like cutting a hamburger with a chainsaw," Gadepally said. "Does it work? Sure… but it definitely is overkill." This doesn't need to be the case. "We have found in many instances that you can use a smaller but tuned model, to achieve similar performance to a much larger model," Gadepally said, noting that this is especially true for new "agentic" systems. "You're often trying thousands of different parameters, or different combinations of things to discover which is the best one, and by being a little bit more intelligent, we could dismiss or essentially terminate a lot of the workloads or a lot of those combinations that weren't getting you towards the right answer."

Each of those unnecessary parameters isn't just a computational dead end, it's another nudge towards rolling blackouts, less potable water and rising utility costs to surrounding communities. As Gadepally said, "We're just building bigger and bigger without thinking about, 'Do we actually need it?'"

About our ads