# Transpiler patches

Transpiler patches executed only once to rewrite IL code of a specific method.
Therefore, transpiler patches themselves cannot depend on runtime state.

Writing pre-patches or transpiler patches is harder because they depend on IL code from 
original game assemblies, obtainable only while running game or by decompiling game DLLs. 
Use transpiler patches only if absolutely required.

Transpiler patches best understood by logging original and modified IL code in separate files. 
Done by `RecordOriginalCode` and `RecordPatchedCode` methods of `TranspilerHelpers` class. 
However, capturing IL code requires running game to capture this information. 
Use it wisely, ask developer for assistance running game to get original IL code and 
to verify your changes. Writing transpiler patches requires systematic iteration. 

Never extend plugin's `Init` method with explicit `harmony.Patch` calls. 
Enough to decorate static patch classes with `[HarmonyPatch]` or `[HarmonyPatch(type(ClassToPatch))]`, 
then properly write its members.