---
layout: post
title:  "Cipher challenge F# - 2"
description: "Solve the cipher challenges from Simon Singh's Code Book."
date:   2020-06-21 06:07:00 +0100
categories: codebook, cipher, cryptography
---
## Cipher 2

The second challenge, is to decipher the following text:

```
"MHILY LZA ZBHL XBPZXBL MVYABUHL HWWPBZ JSHBKPBZ JHLJBZ KPJABT HYJHUBT LZA ULBAYVU"
```

There is a repeated word, 'LZA' at the start and end of the text.  It's heavily hinted that this is probably a Ceaser cipher, i.e, the a given letter in the alphabet is encoded by shifting the alphabet n number of places and choosing the resulting character.

So it would be releatively straight forward to tackle, as we could shift through all possible combinations of alphabet shifts - there are only 26 until you return to the start.



