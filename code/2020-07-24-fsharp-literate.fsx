(**
Literate F#
===============

Up until now, I've mostly written my blog posts directly in markdown, and including code
snippets copied from fsx files.

Literate programming has existed for a while in the F# ecosystem, although I always found
it clunky to use, probably because it hasn't been updated for a while.  However Don Syme 
gave it a refresh last week, which has made it far more usable, especially as a Mac user.

This purpose of this post is to:
* detail how I use Literate within my posts
* remind me how to use it

My Blog
-------
I use GitHub's Jekyll as a 'blog engine'.  This a static blog engine, which means that 
you write posts in markdown, submit to your repository which the blog engine renders in html.

This is works well and F# code is rendered resonably well.

However a few people seems to be using Literate programming and the associated tools in F#
in order to generate html files directly, and then post to Jekyll.

I tool my workflow from Colin Bull's [blog][cb] post, and associated github repository, 
although I updated all dlls to the latest version of FSharp.Formatting.

This file demonstrates how to write literate F# script
files (`*.fsx`) that can be transformed into nice HTML
using the `literate.fsx` script from the [F# Formatting
package](http://fsprojects.github.io/FSharp.Formatting).

As you can see, a comment starting with double asterisk
is treated as part of the document and is transformed 
using Markdown, which means that you can use:

 - Unordered or ordered lists 
 - Text formatting including **bold** and _emphasis_

And numerous other [Markdown][md] features.

 [md]: http://daringfireball.net/projects/markdown
 [cb]: http://www.colinbull.net/2014/11/04/Blogging-with-FSharp/

Writing F# code
---------------
Code that is not inside comment will be formatted as
a sample snippet (which also means that you can 
run it in Visual Studio or MonoDevelop).
*)

/// The Hello World of functional languages!
let rec factorial x = 
  if x = 0 then 1 
  else x * (factorial (x - 1))

let f10 = factorial 10

(**
Hiding code
-----------

If you want to include some code in the source code, 
but omit it from the output, you can use the `hide` 
command.
*)

(*** hide ***)
/// This is a hidden answer
let hidden = 42

(** 
The value will be deffined in the F# code and so you
can use it from other (visible) code and get correct
tool tips:
*)

let answer = hidden

(** 
Moving code around
------------------

Sometimes, it is useful to first explain some code that
has to be located at the end of the snippet (perhaps 
because it uses some definitions discussed in the middle).
This can be done using `include` and `define` commands.

The following snippet gets correct tool tips, even though
it uses `laterFunction`:
*)

(*** include:later-bit ***)

(**
Then we can explain how `laterFunction` is defined:
*)

let laterFunction() = 
  "Not very difficult, is it?"

(**
This example covers pretty much all features that are 
currently implemented in `literate.fsx`, but feel free 
to [fork the project on GitHub][fs] and add more 
features or report bugs!

  [fs]: https://github.com/fsprojects/FSharp.Formatting

*)

(*** define:later-bit ***)
let sample = 
  laterFunction()
  |> printfn "Got: %s"

(**

Other features
--------------

The tool-tips also work for double-backtick identifiers.
This might be useful to generate nice documents from tests:

*)
let ``1 + 1 should be equal to 2``() =
  1 + 1 = 2

(**
Others examples follow here.
*)