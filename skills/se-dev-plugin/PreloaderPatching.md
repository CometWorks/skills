# Preloader patches

Pre-patching done before loading game DLLs. Therefore, preloader patches cannot depend on them. 
Use preloader patch only if you must modify code later inlined by JIT compiler, 
which prevents changing such code by transpiler patches. You must also use pre-patches to 
replace entire interfaces, classes or structs.

Preloader patches process IL code in `Mono.Cecil` format, therefore differ from
transpiler patches. Same code cannot be used for both.

Preloader initialization, copy into plugin's project folder, then customize: `Examples/Client/Preloader.cs`

Example preloader patch: `Examples/Client/DecodePixelDataPrepatch.cs`

Currently, preloader patching available only on game client (Pulsar feature) and not available
on server side (Magnetar).
