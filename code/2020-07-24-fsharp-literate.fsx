(*** raw ***)
---
layout: post
title:  "Literate F#"
description: "Using F# Literate for blog posts on Jekyll."
date:   2020-07-24 06:07:00 +0100
categories: 
tags: F# FSharp Literate Formatting
---

(**
My Blog
-------
I use github's Jekyll as a 'blog engine'.  This means I can write posts in markdown 
and commit to the repository at which point the blog engine renders in nice html.

This works well and F# code is rendered resonably neatly (although it's somewhat hard to 
change the colour of the syntax).

Jekyll is free, easy enough to use.

However, a few people seem to be using Literate programming and the associated tools in F#
to generate html files directly, and then post to Jekyll, which it then displayes on your
blog.

So I decided to give this a crack.  

I based my workflow on Colin Bull's [blog][cb] post, and associated github repository, 
although I updated all dlls to the latest version of FSharp.Formatting.* and used my 
own scripts and css files.

Enter Literate F#
-----------

I've been writing my blog posts directly in markdown, and including code
snippets copied from fsx files, and as stated above, this does seem to work quite well, 
although it means copying code snippets from other files and icluding them as part of the
markdown document.

Literate programming has existed for a while in the F# ecosystem, although I always found
it clunky to use, probably because it hasn't been updated for a while.  However Don Syme
gave it a complete overhaul last week, which has made it far more usable, especially as a Mac
user.

The beauty of Literate programming, is that you can write the code and markdown withint the
same document, e.g. an fsx file.  So you can execute the code directly from the blog post - 
no need to copy and paste.

This purpose of this post is to:

 - detail how I use Literate within my posts.
 - as an aide-memoire when I eventually forget what I did.

FSX
---

The recipe that I follow, is to write the post within a F# script file (.fsx) and then 
convert to html using `FSharp.Formatting.Literate`.

In order for the Jekyll engine to include the html that's generated into your blog
you need to have a 'front matter' section on top of your html, which means that any blog
post generated from fsx files needs to have the following at the top of the fsx file.

```  bash
---
layout: post
title:  "Literate F#"
description: "Using F# Literate for blog posts on Jekyll."
date:   2020-07-24 06:07:00 +0100
categories: 
tags: F# FSharp Literate
---
```
This must be inserted after the 'raw' Literate special [command][cd] `(*** raw ***)`
, in order for the Literate processor to ignore it.  If this doesn't exist on your html page, 
then the Jekyll engine won't include it within your blog.

After this gumph, you can start your post.

Start with a double asterisk comment, which allows you to write standard Markdown.

As as example, you can write lists:

 - Unordered or ordered lists
 - Text formatting including **bold** and _emphasis_ and ```bash commands```

And numerous other [Markdown][md] features.

 [md]: http://daringfireball.net/projects/markdown
 [cb]: http://www.colinbull.net/2014/11/04/Blogging-with-FSharp/
 [cd]: https://fsprojects.github.io/FSharp.Formatting/literate.html

Writing F# code
---------------
Code that is not inside comment will be formatted as a sample snippet
(which also means that you can run it in Visual Studio Code!).

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
This can be achieved through FSharp.Formatting.Literate as follows.

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

//process directory, converting files in code to the _posts directory.
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
If you wanted a once step, post-to-jekyll process, you could include this in a bash script 
that will run this file and commit to your github repository:
``` bash 
#!/bin/bash
dotnet fsi processScript.fsx
git add *
git commit -m "latest changes to blog"
git push
```
*)

(** 
## Template
The html that's generated is raw, and quite ugly, so in order to prettify it, you need to use
a template, with points at a css file that provides the formatting to your page.  This css
file includes the colours to use for the F# syntax highlighting.

In order to use the template directly in the Literate process you can use the following:

*)

//this processes a single file.
let template = source + "template.html"
let in = source + "post.fsx"
let out = source + "post.html"

do Literate.ConvertScriptFile(input = in, template = template, output = out)

(** 
If the template contains the css file, then your output when opened in the brower will
be nice and pretty.

However when creating content for your blog post on Jekyll, you don't need to apply a template.
As Jekyll already embeds your html within the main page template for your post.  But you
do need to ensure that the main css file is uploaded to your Jekyll repository.

The best way to visualise this - and the way that made most sense to me - is to right click 
in your browser and view the page source.  You should be then able to click on the css file 
that I used and see yourself what settings I used to prettify the output.

I don't come from a web development background, css is new to me, so I found viewing the
source in the brower and tinkering with the css to be valuable in order to visualise the 
impact the css had on the page.
*)

