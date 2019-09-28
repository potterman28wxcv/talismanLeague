Now that we have the logic to transform a non-valid solution into a valid one without modifying the tables too much, we should implement a better "initial solution" to work with.

Possible trick: put the strongest "Friday only" and the strongest "Sunday only" player in two separate tables, then.. work from that. Step by step, for each of these players, add the "closest member" in terms of score in the adequate table.

On a first approximation, do it irrelevantly of the available days. And then feed it to our correction algorithm.

If that doesn't work out, take into account the available days..
