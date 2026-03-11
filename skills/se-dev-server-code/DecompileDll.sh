#!/bin/sh

# $1 is the first argument (directory name)
# $2 is the second argument (path to DLL)

echo "Decompiling: $1"

# Check if the directory already exists
if [ -d "Decompiled/$1" ]; then
    echo "Directory Decompiled/$1 already exists. Skipping."
else
    # First ilspycmd execution to decompile to C# code
    ilspycmd --project --nested-directories --referencepath Bin64 --languageversion CSharp11_0 --disable-updatecheck -o "Decompiled/$1" "$2"
    if [ $? -ne 0 ]; then
        echo "Failed during project decompilation."
        exit 1
    fi

    # Second ilspycmd execution to decompile to IL code
    # Uncomment the next line to produce IL code. These files are big and useful only for transpiler and preloader patch development.
    #ilspycmd --ilcode --il-sequence-points -o "Decompiled/$1" "$2"
    if [ $? -ne 0 ]; then
        echo "Failed during IL code generation."
        exit 1
    fi
fi

exit 0