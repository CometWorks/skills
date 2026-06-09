# Preloader patches

Pre-patching is done before loading the game DLLs. Therefore, preloader patches cannot depend on them. 
Use a preloader patch only if you must modify code which is then later inlined by the JIT compiler, 
which prevents changing such code by transpiler patches. You must also use pre-patches if you want to 
replace entire interfaces, classes or structs.

Preloader patches process IL code in the `Mono.Cecil` format, therefore they are different from
transpiler patches. The same code cannot be used for both.

Preloader initialization, copy into the plugin's project folder, then customize: `Examples/Client/Preloader.cs`

Example preloader patch: `Examples/Client/DecodePixelDataPrepatch.cs`

Currently, preloader patching is available only on the game client (Pulsar feature) and not available
on the server side (Magnetar).
