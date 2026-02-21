#!/bin/sh

LOG="Decompile.log"

echo "Decompiling game assemblies..."
echo "Decompiling game assemblies: " > "$LOG"

# Helper function to run the decompile and handle errors
run_decompile() {
    # Calls your previously converted script
    ./DecompileDll.sh "$1" "$2" >> "$LOG" 2>&1
    
    if [ $? -ne 0 ]; then
        echo "Failed to decompile $1. Please check $LOG for details."
        exit 1
    fi
}

# Execution List
run_decompile "Sandbox.Common" "Bin64/Sandbox.Common.dll"
run_decompile "Sandbox.Game" "Bin64/Sandbox.Game.dll"
run_decompile "Sandbox.Game.XmlSerializers" "Bin64/Sandbox.Game.XmlSerializers.dll"
run_decompile "Sandbox.Graphics" "Bin64/Sandbox.Graphics.dll"
run_decompile "Sandbox.RenderDirect" "Bin64/Sandbox.RenderDirect.dll"
run_decompile "SpaceEngineers" "Bin64/SpaceEngineers.exe"
run_decompile "SpaceEngineers.Game" "Bin64/SpaceEngineers.Game.dll"
run_decompile "SpaceEngineers.ObjectBuilders" "Bin64/SpaceEngineers.ObjectBuilders.dll"
run_decompile "SpaceEngineers.ObjectBuilders.XmlSerializers" "Bin64/SpaceEngineers.ObjectBuilders.XmlSerializers.dll"
run_decompile "VRage.Ansel" "Bin64/VRage.Ansel.dll"
run_decompile "VRage.Audio" "Bin64/VRage.Audio.dll"
run_decompile "VRage" "Bin64/VRage.dll"
run_decompile "VRage.EOS" "Bin64/VRage.EOS.dll"
run_decompile "VRage.EOS.XmlSerializers" "Bin64/VRage.EOS.XmlSerializers.dll"
run_decompile "VRage.Game" "Bin64/VRage.Game.dll"
run_decompile "VRage.Game.XmlSerializers" "Bin64/VRage.Game.XmlSerializers.dll"
run_decompile "VRage.Input" "Bin64/VRage.Input.dll"
run_decompile "VRage.Library" "Bin64/VRage.Library.dll"
run_decompile "VRage.Math" "Bin64/VRage.Math.dll"
run_decompile "VRage.Math.XmlSerializers" "Bin64/VRage.Math.XmlSerializers.dll"
run_decompile "VRage.Mod.Io" "Bin64/VRage.Mod.Io.dll"
run_decompile "VRage.NativeAftermath" "Bin64/VRage.NativeAftermath.dll"
run_decompile "VRage.NativeWrapper" "Bin64/VRage.NativeWrapper.dll"
run_decompile "VRage.Network" "Bin64/VRage.Network.dll"
run_decompile "VRage.Platform.Windows" "Bin64/VRage.Platform.Windows.dll"
run_decompile "VRage.Render" "Bin64/VRage.Render.dll"
run_decompile "VRage.Render11" "Bin64/VRage.Render11.dll"
run_decompile "VRage.Scripting" "Bin64/VRage.Scripting.dll"
run_decompile "VRage.Steam" "Bin64/VRage.Steam.dll"
run_decompile "VRage.UserInterface" "Bin64/VRage.UserInterface.dll"
run_decompile "VRage.XmlSerializers" "Bin64/VRage.XmlSerializers.dll"

# Success cleanup
echo "Successfully decompiled the game assemblies."
rm "$LOG"
exit 0