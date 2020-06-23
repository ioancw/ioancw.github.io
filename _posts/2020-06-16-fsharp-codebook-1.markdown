---
layout: post
title:  "Cipher challenge F#"
description: "Solve the cipher challenges from Simon Singh's Code Book."
date:   2020-06-18 06:07:00 +0100
categories: 
---
# Cipher Challenges

In the summer of 2000, about 20 years ago, I read [The Code Book][the-code-book] by Simon Singh, which charts the history of code breaking from Caesar through to Quantum Computing.

At the end of the book, the author provided 10 Cipher Challenges, with a prize of £10,000 awarded to the person/team that solved all 10 challenges.  For some reason (I don't remember why), I didn't attempt the challenge and quickly forgot about them.  

However, a few years ago I picked up the book again, and managed to solve the first few using Python (the first two or three aren't particularly hard), but sadly lost interest again.

Anyway I've decied to have another crack (pun intended), but this time using F#.

You don't have to buy the book in order to try the challenges, as the ciphertexts are available on the author's website.

The challenge was officially solved in Oct 2000, by a team of Swedish [researchers][swedish-solution], so sadly the prize money has already been awarded.

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

There isn't much one can say about this, other than some cipher words look repeated, e.g. JPX and MTN.  Could these be 'the' and 'and' respectively.  I'm assuming that as these words aren't repeated the cipher isn't very fancy, and so the first plan of attack would be a letter frequency analysis.

You can easily google letter frequencies for various languages, and you can see that 'e' is the most frequent letter in the english language - that's why its represented by a single dot in morse code.

So a simple frequency analysis can propbably be done with pen and paper, however it would be rather pointless to do this in when talking about coding it in F#.

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
ri toe sawe ongh cawe fnhto friuehs nf a wai's oaid, aid mhnte nveh auarist toe 
caidlestrcy gpni toe plasteh nf toe mall nf toe yriu's palace; aid toe yriu sam 
toe paht nf toe oaid toat mhnte. toei toe yriu's cngiteiaice mas coaiued, aid ors 
tonguots thngbled orw, sn toat toe xnrits nf ors lnris mehe lnnsed, aid ors yiees 
swnte nie auarist aintoeh. toe yriu chred alngd tn bhriu ri toe asthnlnuehs, toe 
coaldeais, aid toe snntosakehs. aid toe yriu spaye, aid sard tn toe mrse wei nf 
babklni, monsneveh soall head tors mhrtriu, aid sonm we toe ritehphetatrni 
toehenf, soall be clntoed mrto sca
```
The convention is cryptography is to use UPPER case for the ciphertext and lower case for the paintext (i.e. the decrypted text).

Looking at the plaintext above, the second word of the first line (also second word on second line) could be a 'the', thus indicating that the o should have been decryped as an h instead.  So this requires us to change P to h and Y to o in the key map.  Running the decypher function again, we get:
``` fsharp
let key3 =
    [ ('X', 'e')
      ('J', 't')
      ('M', 'a')
      ('P', 'h')
      ('T', 'i')
      ('C', 'n')
      ('R', 's')
      ('B', 'r')
      ('V', 'o')
      ('N', 'd')
      ('G', 'l')
      ('W', 'u')
      ('A', 'c')
      ('Y', 'm')
      ('I', 'f')
      ('H', 'y')
      ('L', 'w')
      ('U', 'g')
      ('Q', 'p')
      ('F', 'b')
      ('D', 'v')
      ('E', 'k')
      ('S', 'x') ]

key3 |> decipher
``` 
```
ri the sawe hngo cawe fnoth friueos nf a wai’s haid, aid monte nveo auarist the 
caidlestrcy gpni the plasteo nf the mall nf the yriu’s palace; aid the yriu sam 
the paot nf the haid that monte. thei the yriu’s cngiteiaice mas chaiued, aid hrs 
thnguhts tongbled hrw, sn that the xnrits nf hrs lnris meoe lnnsed, aid hrs yiees 
swnte nie auarist aintheo. the yriu cored alngd tn boriu ri the astonlnueos, the 
chaldeais, aid the snnthsakeos. aid the yriu spaye, aid sard tn the mrse wei nf 
babklni, mhnsneveo shall oead thrs mortriu, aid shnm we the riteopoetatrni 
theoenf, shall be clnthed mrth sca
```
This looks more resonable, although we can make futher guesses.  'Cawe' look as if it should be 'same', L should be m and Y is w.  Also 'aid' could be 'and', so T is n and C is i (given the are adjacent in the frequency analysis we probably got them the wrong way around).

Trying again gives us:
``` fsharp
let key4 =
    [ ('X', 'e')
      ('J', 't')
      ('M', 'a')
      ('P', 'h')
      ('T', 'n')
      ('C', 'i')
      ('R', 's')
      ('B', 'r')
      ('V', 'o')
      ('N', 'd')
      ('G', 'l')
      ('W', 'u')
      ('A', 'c')
      ('Y', 'w')
      ('I', 'f')
      ('H', 'y')
      ('L', 'm')
      ('U', 'g')
      ('Q', 'p')
      ('F', 'b')
      ('D', 'v')
      ('E', 'k')
      ('S', 'x') ]

key4 |> decipher
```
```
rn the same higo came fioth frnueos if a man’s hand, and woite iveo auarnst the 
candlestrcy gpin the plasteo if the wall if the yrnu’s palace; and the yrnu saw 
the paot if the hand that woite. then the yrnu’s cigntenance was chanued, and hrs 
thiguhts toigbled hrm, si that the xirnts if hrs lirns weoe liised, and hrs ynees 
smite ine auarnst anitheo. the yrnu cored aligd ti bornu rn the astoiliueos, the 
chaldeans, and the siithsakeos. and the yrnu spaye, and sard ti the wrse men if 
babklin, whisieveo shall oead thrs wortrnu, and shiw me the rnteopoetatrin 
theoeif, shall be clithed wrth sca
```
Which is better and it's starting to look a lot like English, possibly referring to something biblical in nature.
Maybe 'fioth' should be 'forth', so chaniging the map accordingly gives us:
``` fsharp
let key5 =
    [ ('X', 'e')
      ('J', 't')
      ('M', 'a')
      ('P', 'h')
      ('T', 'n')
      ('C', 'o')
      ('R', 's')
      ('B', 'i')
      ('V', 'r')
      ('N', 'd')
      ('G', 'l')
      ('W', 'u')
      ('A', 'c')
      ('Y', 'w')
      ('I', 'f')
      ('H', 'y')
      ('L', 'm')
      ('U', 'g')
      ('Q', 'p')
      ('F', 'b')
      ('D', 'v')
      ('E', 'k')
      ('S', 'x') ]

key5 |> decipher
```
```
in the same hogr came forth finuers of a man’s hand, and wrote over auainst the 
candlesticy gpon the plaster of the wall of the yinu’s palace; and the yinu saw 
the part of the hand that wrote. then the yinu’s cogntenance was chanued, and his 
thoguhts trogbled him, so that the xoints of his loins were loosed, and his ynees 
smote one auainst another. the yinu cried alogd to brinu in the astrolouers, the 
chaldeans, and the soothsakers. and the yinu spaye, and said to the wise men of 
babklon, whosoever shall read this writinu, and show me the interpretation 
thereof, shall be clothed with sca
```
This is definately looking more biblical in nature.
Looking through the plain text again, there are a few words that should have letters changed, e.g. 'hogr' could be 'hour' and 'finuers' should be 'fingers', thus giving us the following (omiting the F# code this time):
```
in the same hour came forth fingers of a man’s hand, and wrote over against the 
candlesticy upon the plaster of the wall of the ying’s palace; and the ying saw 
the part of the hand that wrote. then the ying’s countenance was changed, and his 
thoughts troubled him, so that the xoints of his loins were loosed, and his ynees 
smote one against another. the ying cried aloud to bring in the astrologers, the 
chaldeans, and the soothsakers. and the ying spaye, and said to the wise men of 
babklon, whosoever shall read this writing, and show me the interpretation 
thereof, shall be clothed with sca
```
Reading through the plaintext again, it mostly makes sense, however 'ying' should be 'king', making the change to the key map, give us the following plaintext.
```
in the same hour came forth fingers of a man's hand, and wrote over against the 
candlestick upon the plaster of the wall of the king's palace; and the king saw 
the part of the hand that wrote. then the king's countenance was changed, and his 
thoughts troubled him, so that the xoints of his loins were loosed, and his knees 
smote one against another. the king cried aloud to bring in the astrologers, the 
chaldeans, and the soothsayers. and the king spake, and said to the wise men of 
babylon, whosoever shall read this writing, and show me the interpretation 
thereof, shall be clothed with sca
```

This looks fully decrypted now as it's readable in the plaintext for (albeit for a few old English words).

[the-code-book]: https://www.amazon.co.uk/Code-Book-Secret-History-Code-breaking/dp/1857028899/ref=sr_1_1?adgrpid=52694659589&dchild=1&gclid=EAIaIQobChMIx_fC3euG6gIVE-3tCh1PQw-9EAAYASAAEgKwwPD_BwE&hvadid=259082330636&hvdev=c&hvlocphy=1002316&hvnetw=g&hvqmt=e&hvrand=2287691142347200337&hvtargid=kwd-301205216858&hydadcr=28148_1752695&keywords=the+code+book&qid=1592327926&sr=8-1&tag=googhydr-21
[swedish-solution]: http://codebook.org

