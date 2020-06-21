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
