---
layout: post
title:  "Starting with F#"
description: "The adventure with F# begins."
date:   2019-02-10 06:07:00 +0100
categories: 
---
## Introduction

I'm learning F# for work, so these are some notes that I've made up along the way.

``` fsharp
type ShoppingCart =
    | EmptyCart  // no data
    | ActiveCart of ActiveCartData
    | PaidCart of PaidCartData
```