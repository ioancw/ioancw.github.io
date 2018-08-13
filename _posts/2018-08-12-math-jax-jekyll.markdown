---
layout: post
title:  "Using MathJax on Jekyll"
date:   2018-08-12 06:07:00 +0100
categories: 
math: true
---
## Introduction

This post will describe how to use MathJax to generate $$x^2$$, or $$\mathbf{X} = \mathbf{Z} \mathbf{P^\mathsf{T}}$$

and

$$
a^2 + b^2 = c^2
$$
### MathJax setup.

* I followed the steps from [Dason][jekyll-mathjax] on his blog and also [here][gaston].  Although I had to use default.html rather than the page.html.

This was overly fiddly to setup (seems par for the course, based on other comments), e.g. the maths rendering worked when I served locally, however when I merged to GitHub, the math wasn’t rendered on the live site.  

Turns out one had to use `https` instead of `http` in the website included in the `default.html` file.  See Dason’s blog above.

There isn’t one global way of doing this, each blog on the subject seems to offer contradicting advice.  So some fiddling and testing will be required.

If you can see something below, then it has worked):

$$
e^{i\pi} + 1 = 0
$$

[jekyll-mathjax]: http://dasonk.com/blog/2012/10/09/Using-Jekyll-and-Mathjax
[gaston]:http://www.gastonsanchez.com/visually-enforced/opinion/2014/02/16/Mathjax-with-jekyll/
