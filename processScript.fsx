#I "tools"
#r "FSharp.Formatting.Common.dll"
#r "FSharp.Formatting.Markdown.dll"
#r "FSharp.Formatting.Literate.dll"
#r "FSharp.Formatting.CodeFormat.dll"

open FSharp.Formatting.Literate
open System.IO

let source = __SOURCE_DIRECTORY__

let codeDirectory = source + "/code"
let outputDirectory = source + "/_posts"


//process directory, moving files from code to the _posts directory.
let processDirectory () =
    let outputKind = OutputKind.Html  
    let inputs = Directory.GetFiles(codeDirectory, "*")
    for input in inputs do
        let baseName = Path.GetFileNameWithoutExtension(input)
        let outputFile = Path.Combine(outputDirectory, sprintf "%s.%s" baseName outputKind.Extension)
        printfn "converting %s --> %s" input outputFile
        Literate.ConvertScriptFile(input = input, output = outputFile)

do processDirectory ()
