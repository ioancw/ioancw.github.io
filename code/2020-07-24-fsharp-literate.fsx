(*** raw ***)
---
layout: post
title:  "Literate F#"
description: "Using F# Literate for blog posts on Jekyll."
date:   2020-07-24 06:07:00 +0100
categories: 
---

(**
Literate F#
-----------

Up until now, I've mostly written my blog posts directly in markdown, and including code
snippets copied from fsx files.

Literate programming has existed for a while in the F# ecosystem, although I always found
it clunky to use, probably because it hasn't been updated for a while.  However Don Syme
gave it a refresh last week, which has made it far more usable, especially as a Mac user.

This purpose of this post is to:

 - detail how I use Literate within my posts.
 - remind me how to use it, when I forget.

My Blog
-------
I use github's Jekyll as a 'blog engine'.  This a static blog engine, which means that
you write posts in markdown and submit to your repository which the blog engine renders in html.

This works well and F# code is rendered resonably neatly (although it's somewhat hard to 
the colour of the syntax.)

However a few people seem to be using Literate programming and the associated tools in F#
in order to generate html files directly, and then post to Jekyll.

I based my workflow from Colin Bull's [blog][cb] post, and associated github repository,
although I updated all dlls to the latest version of FSharp.Formatting.* and used my own 
scripts and css times.

FSX
---

The recipe that I follow, is to write the post within a F# script file (.fsx) and then 
conver to html using FSharp.Formatting.Literate.

Start with a double asterisk comment, which allows you to write standard Markdown.

As as example, you can write lists:

 - Unordered or ordered lists
 - Text formatting including **bold** and _emphasis_

And numerous other [Markdown][md] features.

 [md]: http://daringfireball.net/projects/markdown
 [cb]: http://www.colinbull.net/2014/11/04/Blogging-with-FSharp/

Writing F# code
---------------
Code that is not inside comment will be formatted as a sample snippet
(which also means that you can run it in Visual Studio Code or editor of your choosing).
*)

/// The Hello World of functional languages!
let rec factorial x =
    if x = 0 then 1 else x * (factorial (x - 1))

let f10 = factorial 10

(** 
You can then write more blog content.  And also some more code:
*)

let rec listToString l = 
  match l with
  | [] -> ""
  | head :: tail -> head.ToString() + listToString tail

(** 
Posting to blog
--------------

Before posting to my blog repository on github, we need to convert from fsx to a html file.
This can be achieved through FSharp.Formatting.Literate as such.

Create a new fsx file with the following content.
*)

#I "../tools"
#r "FSharp.Formatting.Common.dll"
#r "FSharp.Formatting.Markdown.dll"
#r "FSharp.Formatting.Literate.dll"
#r "FSharp.Formatting.CodeFormat.dll"

open FSharp.Formatting.Literate

let source = __SOURCE_DIRECTORY__

let codeDirectory = source + "/code"
let outputDirectory = source + "/_posts"

//process directory, moving files from code to the _posts directory.
let processDirectory () =
    Literate.ConvertDirectory(input = codeDirectory, outputDirectory = outputDirectory)

do processDirectory ()

(** 
This assumes that: 

 - the dlls are in the tools directory
 - fsx files are in the code directory
 - generated html files will be in the _posts directory

The script will process all fsx files in the code directory and create the html files in
the _posts directory.

You can then run the script from the command line as follows
``` bash
dotnet fsi yourscriptname.fsx
```
You dan then write a bash script, in order to commit your files to github.
*)