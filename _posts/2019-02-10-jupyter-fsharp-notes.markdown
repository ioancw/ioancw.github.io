---
layout: post
title:  "Bin packing with F#"
description: "The adventure with F# begins."
date:   2019-02-10 06:07:00 +0100
categories: 
---
## Bin packing

A colleage recently asked me to test out one of his interview questions, which went something like:

"Pack n number of items of different volumes v into boxes of volume V, and do so by minimising the number of boxes used."  Each item fits into a box, i.e. v <= V

I started to think about this problem, by thinking of 10 boxes `[1,2,3,4,5,6,7,8,9,10]`, where the int value represents the volume of each item, and tried to 'fit' them into boxes of Volume 10.

Naively, starting at the front of the list and adding to the next available box (including the current box, if not full), gives us the following packed boxes:

    [1,2,3,4] -> volume = 10
    [5] -> volume = 5
    [6] -> volume = 6
    [7] -> volume = 7
    [8] -> volume = 8
    [9] -> volume = 9
    [10] -> volume = 10

This isn't particularly good and means we've packed our items into 7 boxes.

Another approach is to sort the initial list of boxes in decreasing order of their volume.
In this case, we get the following list of boxes:

`[10,9,8,7,6,5,4,3,2,1]`

And by following the same algorithm as above, we pack into 6 boxes:

    [10] -> volume = 10
    [9,1] -> volume = 10
    [8,2] -> volume = 10
    [7,3] -> volume = 10
    [6,4] -> volume = 10
    [5] -> volume = 5

Which is one fewer box that the first example.

We try to pack a given item into the first box that's available, which means that the 1 is paired with the 9, the 2 with 8 and so on.

Googling lead me to read the following in a paper trying to optimise (i.e lower) the numbers of bins (or boxes) used to pack items.

What I've done, is simulate packing 90 randomly chosen boxes, that range in volume between 1 and 1,000,000 units.  I've run the simulation 1,000,000 times, and provided the average number of boxes used to pack the 90 items.

``` fsharp
open FSharp.Collections.ParallelSeq
open System

let packBoxes items volume =
    let mutable boxes = [||]
    items
    |> Array.sortDescending
    |> Array.iter (fun box ->
        let sackIndex =
            boxes
            |> Array.tryFindIndex (fun sack -> sack + box <= volume)

        match sackIndex with
        | Some index -> boxes.[index] <- boxes.[index] + box
        | None ->
            Array.Resize(&boxes, Array.length boxes + 1)
            boxes.[Array.length boxes - 1] <- box)
    Array.length boxes
```
The above defines a function that takes a number of items to pack into boxes of max volume, volume.
Returning the number of boxes 

Now we need to run the simulation of 90 boxes of random volumes.

``` fsharp
let randomItems from upTo times =
    let randy = Random()
    Array.init times (fun _ -> randy.Next(from, upTo))

let stopWatch = System.Diagnostics.Stopwatch.StartNew()
let vol = 1000000

let simulation4 =
    PSeq.fold (fun acc _ -> (packBoxes (randomItems 1 vol 90) vol) + acc) 0 { 0 .. vol }

stopWatch.Stop()

let averageSacks = (float) simulation4 / (float) vol
printfn "Average number of sacks used %f" averageSacks
printfn "%i" stopWatch.Elapsed.Seconds

```

This gives the average number of boxes you can pack the 90 items into, to be just over half the number of items, at 47.59 boxes.

I tried to performance tune the script, in order to get a performance which was comparible to Julia.
I ran the same simulation in Julia in approx. 8 seconds.

The simulation in F# took approx 16 seconds (when running the simulation in parallel).
My original implementation (which didn't use a mutable array), and created a list of 1,000,000 random boxes, took approximately 4 minutes, so a reduction to 16 seconds isn't too bad.  

I also did a naive implementation in Python which took nearly 8 minutes to run (but I havnen't tried to optimise this)

All the above was run on my 15inch 6 core Macbook Pro (2018 version).

One can run this script on the command line, in Mac OS, using:

``` bash
fsharpi binpacking.fsx
```

