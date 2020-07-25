#I "tools"
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
