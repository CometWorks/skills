#!/bin/sh

# $1 is the first argument (directory name)
# $2 is the second argument (path to DLL)

# Some XmlSerializers assemblies have very deep generic type graphs that blow
# the default 1 MB managed thread stack inside ilspycmd ("Recursion too deep;
# the stack overflowed", 0xC00000FD). Bump the .NET default stack size to 16 MB
# (16x the default) for every thread the runtime creates. The variable is read
# by the CoreCLR host in hex bytes; 0x1000000 = 16777216 = 16 MB.
export DOTNET_Thread_DefaultStackSize=1000000
export COMPlus_Thread_DefaultStackSize=1000000

OUT="Data/Decompiled/$1"

echo "Decompiling: $1"

# A successful previous run leaves the marker file. The marker is what makes
# subsequent runs skip the assembly cleanly even if the source set was wiped
# only partially.
if [ -f "$OUT/.decompiled" ]; then
    echo "Directory $OUT already decompiled. Skipping."
    exit 0
fi

# If a partial directory is left over from an earlier failed/aborted run,
# remove it so ilspycmd can produce a clean tree.
if [ -d "$OUT" ]; then
    echo "Removing stale partial decompilation in $OUT"
    rm -rf "$OUT"
fi

ilspycmd --project --nested-directories --referencepath Bin64 --languageversion CSharp11_0 --disable-updatecheck -o "$OUT" "$2"
RC=$?
if [ $RC -ne 0 ]; then
    echo "Failed during project decompilation (ilspycmd exit $RC)."
    rm -rf "$OUT"
    exit 1
fi

# Second ilspycmd execution to decompile to IL code
# Uncomment the next line to produce IL code. These files are big and useful only for transpiler and preloader patch development.
#ilspycmd --ilcode --il-sequence-points -o "$OUT" "$2"
#RC=$?
#if [ $RC -ne 0 ]; then
#    echo "Failed during IL code generation (ilspycmd exit $RC)."
#    rm -rf "$OUT"
#    exit 1
#fi

# Mark this assembly's decompilation as successful.
touch "$OUT/.decompiled"
exit 0
