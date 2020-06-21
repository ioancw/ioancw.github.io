---
layout: post
title:  "Cipher challenge F#"
description: "Solve the cipher challenges from Simon Singh's Code Book."
date:   2020-06-14 06:07:00 +0100
categories: 
---
# Cipher Challenges

In the summer of 2000, about 20 years ago I read [The Code Book][the-code-book] by Simon Singh, which charts the history of code breaking from Ceaser through to Quantum Computing.

At the end of the book, the author provided 10 Cipher Challenges, where a prize of £10,000 would be awarded to the person/team that solved all 10 challenges.  For some reason (I don't remember why), I didn't attempt the challenge myself and quickly forgot about them.  A few years ago a managed to solve the first few using Python (the first two or three aren't particularly hard), but lost interest again.

Anyway I've decied to have another crack (pun intended), but this time using F#.

You don't have to buy the book in order to try the challenges, as the ciphertexts are available on the author's website.

The challenge was officially solved in Oct 2000, by a team of Swedish [researchers][swedish-solution].

## Cipher 1

The cipher text given by Simon for part1 is:

```
BT JPX RMLX PCUV AMLX ICVJP IBTWXVR CI M LMT’R PMTN, MTN YVCJX CDXV MWMBTRJ JPX
AMTNGXRJBAH UQCT JPX QGMRJXV CI JPX YMGG CI JPX HBTW’R QMGMAX; MTN JPX HBTW RMY
JPX QMVJ CI JPX PMTN JPMJ YVCJX. JPXT JPX HBTW’R ACUTJXTMTAX YMR APMTWXN, MTN PBR
JPCUWPJR JVCUFGXN PBL, RC JPMJ JPX SCBTJR CI PBR GCBTR YXVX GCCRXN, MTN PBR HTXXR
RLCJX CTX MWMBTRJ MTCJPXV. JPX HBTW AVBXN MGCUN JC FVBTW BT JPX MRJVCGCWXVR, JPX
APMGNXMTR, MTN JPX RCCJPRMEXVR. MTN JPX HBTW RQMHX, MTN RMBN JC JPX YBRX LXT CI
FMFEGCT, YPCRCXDXV RPMGG VXMN JPBR YVBJBTW, MTN RPCY LX JPX BTJXVQVXJMJBCT
JPXVXCI, RPMGG FX AGCJPXN YBJP RAM
```

There isn't much one can say about this, other than some cipher words look repeated, e.g. JPX and MTN.  Could these be 'the' and 'and' respectively.  I'm assuming that given these words are repeated the cipher isn't very fancy, and so the first plan of attach would be a letter frequency analysis.

You can easily google letter frequencies for various languages, and you can see that e is the most frequent letter in the english language - that's why its represented by a single dot in morse code.

So a simple frequency analysis can be propbably be done with pen and paper, how ever it would be rather pointless to do this in when talking about coding it in F#.

So we need to write a function to calculate the letter counts across the cipher texts, and then we'll assume that the frequency distribution is the same as our table.

To do this in code we can:

``` fsharp
let cipherText = "BT JPX RMLX PCUV AMLX ICVJP IBTWXVR CI M LMT’R PMTN, MTN YVCJX CDXV MWMBTRJ JPX
  AMTNGXRJBAH UQCT JPX QGMRJXV CI JPX YMGG CI JPX HBTW’R QMGMAX; MTN JPX HBTW RMY
  JPX QMVJ CI JPX PMTN JPMJ YVCJX. JPXT JPX HBTW’R ACUTJXTMTAX YMR APMTWXN, MTN PBR
  JPCUWPJR JVCUFGXN PBL, RC JPMJ JPX SCBTJR CI PBR GCBTR YXVX GCCRXN, MTN PBR HTXXR
  RLCJX CTX MWMBTRJ MTCJPXV. JPX HBTW AVBXN MGCUN JC FVBTW BT JPX MRJVCGCWXVR, JPX
  APMGNXMTR, MTN JPX RCCJPRMEXVR. MTN JPX HBTW RQMHX, MTN RMBN JC JPX YBRX LXT CI
  FMFEGCT, YPCRCXDXV RPMGG VXMN JPBR YVBJBTW, MTN RPCY LX JPX BTJXVQVXJMJBCT
  JPXVXCI, RPMGG FX AGCJPXN YBJP RAM"

let englishLanguageLetterFrequencies =
    [ 'e'; 't'; 'a'; 'o'; 'i'; 'n'; 's'; 'r'; 'h'; 'd'; 'l'; 'u'; 'c'; 'm'; 'f'; 'y';
      'w'; 'g'; 'p'; 'b'; 'v'; 'k'; 'x'; 'q'; 'j'; 'z' ]

let alphabet = [ 'A' .. 'Z' ]

//now get letter frequencies from input cipher text
let frequencies =
    cipherText
    |> Seq.toList //can use regex here
    |> Seq.filter (fun x -> Seq.contains x alphabet) //assuming spaces weren't encrypted.
    |> Seq.groupBy id
    |> Seq.map (fun (l, ls) -> l, Seq.length ls)
    |> Seq.sortByDescending snd
    |> Seq.map fst
```
This yield the collowing letter frequencies in the cipher text, in order of frequencies from highest to lowerst:
```
X, J, M, P, T, C, R, B, V, N, G, W, A, Y, I, H, L, U, Q, F, D, E, S
```
So we can assume that X is the most frequent and therefore is e, J is next and is t, etc.

This can be easily achieved in F# by zipping the arrays (like zipping your flies up):

``` fsharp
let key1 =
    Seq.zip frequencies englishLanguageLetterFrequencies
```
Which gives:
```
X -> e
J -> t
M -> a
P -> o
T -> i
C -> n
R -> s
B -> r
V -> h
N -> d
G -> l
W -> u
A -> c
Y -> m
I -> f
H -> y
L -> w
U -> g
Q -> p
F -> b
D -> v
E -> k
S -> x
```

We next need to write a function that will apply this 'key', essentially converting an ecrypted character X to a decrypted character e:

```fsharp
let decipher (charMap: seq<char * char>) =
  charMap
  |> Seq.fold (fun (state: string) (c, p) -> state.Replace(c, p)) cipherText

```
The frist time this is run we get the following plaintext. 
```
ri toe sawe ongh cawe fnhto friuehs nf a wai���s oaid, aid mhnte nveh auarist toe caidlestrcy gpni toe plasteh nf toe mall nf toe yriu���s palace; aid toe yriu sam toe paht nf toe oaid toat mhnte. toei toe yriu���s cngiteiaice mas coaiued, aid ors tonguots thngbled orw, sn toat toe xnrits nf ors lnris mehe lnnsed, aid ors yiees swnte nie auarist aintoeh. toe yriu chred alngd tn bhriu ri toe asthnlnuehs, toe coaldeais, aid toe snntosakehs. aid toe yriu spaye, aid sard tn toe mrse wei nf babklni, monsneveh soall head tors mhrtriu, aid sonm we toe ritehphetatrni toehenf, soall be clntoed mrto sca
```
The convention is cryptography is to use 


[the-code-book]: https://www.amazon.co.uk/Code-Book-Secret-History-Code-breaking/dp/1857028899/ref=sr_1_1?adgrpid=52694659589&dchild=1&gclid=EAIaIQobChMIx_fC3euG6gIVE-3tCh1PQw-9EAAYASAAEgKwwPD_BwE&hvadid=259082330636&hvdev=c&hvlocphy=1002316&hvnetw=g&hvqmt=e&hvrand=2287691142347200337&hvtargid=kwd-301205216858&hydadcr=28148_1752695&keywords=the+code+book&qid=1592327926&sr=8-1&tag=googhydr-21
[swedish-solution]: http://codebook.org

