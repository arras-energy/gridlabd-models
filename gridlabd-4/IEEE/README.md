IEEE Network Models
-------------------

The IEEE network models are static GridLAB-D versions of the standard IEEE networks. They do not include any features which would cause the clock to advanced. In particular,

1. All devices controls are set to `MANUAL`.

2. No recorders, players, schedules, or climate objects are included.

3. No clock directive is included.

Caveat: the models generate warnings of various kinds. 

| Model | Description |
| ----- | ----------- |
| 13.glm | This circuit model is very small and used to test common features of distribution analysis software, operating at 4.16 kV. It is characterized by being short, relatively highly loaded, a single voltage regulator at the substation, overhead and underground lines, shunt capacitors, an in-line transformer, and unbalanced loading. |
| 37.glm | This feeder is an actual feeder in California, with a 4.8 kV operating voltage. It is characterized by delta configured, all line segments are underground, substation voltage regulation is two single-phase open-delta regulators, spot loads, and very unbalanced. This circuit configuration is fairly uncommon. |
| 123.glm | The IEEE 123 node test feeder operates at a nominal voltage of 4.16 kV. While this is not a popular voltage level it does provide voltage drop problems that must be solved with the application of voltage regulators and shunt capacitors. This circuit is characterized by overhead and underground lines, unbalanced loading with constant current, impedance, and power, four voltage regulators, shunt capacitor banks, and multiple switches.This circuit is “well-behaved” with minimal convergence problems. |
| 342.glm | The majority of end-use customers in North America are served by radially operated distribution feeders. But in areas where there is a high load density and a need for very high reliability, Low Voltage Network (LVN) systems have been built. LVNs are fundamentally different in design and operation from typical radial distribution feeders and these differences require different methods for computational analysis. The network test system is representative of low voltage network systems that are deployed in urban cores in North America. The power system in an urban core and can be a combination of spot networks and grid networks. Note that this system is NOT an actual circuit, but rather representative of the LVN systems. |
| 8500 glm | Will your algorithm scale up to large problems? Try it on this test feeder. 2500 primary (MV) buses, 4800 total buses including secondaries (LV) and loads. 1-, 2-, 3-phase and split-phase circuits yielding over 8500 total node points. |

References:

* IEEE PES Test Feeders, URL: https://cmte.ieee.org/pes-testfeeders/resources/
