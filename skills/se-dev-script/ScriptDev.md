# ScriptDev Plugin for Space Engineers

This plugin automatically updates code in programmable blocks
whenever corresponding `Script.cs` changes. Detected based
on file's last modification time, polled every second.

Scripts of more than 100,000 characters can be loaded. Useful
for offline development, but not compatible with multiplayer.

Please consider supporting my work on [Patreon](https://www.patreon.com/semods) or one time via [PayPal](https://www.paypal.com/paypalme/vferenczi/).

*Thank you and enjoy!*

## Prerequisites

- [Space Engineers](https://store.steampowered.com/app/244850/Space_Engineers/)
- [Pulsar](https://github.com/SpaceGT/Pulsar)

## Usage

Enable the **ScriptDev** plugin in Pulsar, apply change and restart game.

PB name must include script's name in square brackets.
For example: `Programmable Block [Name Of My Script]`

Script subdirectories also work, separate them by forward slashes.
For example: `Programmable Block [Script Subdir/Name Of My Script]`

Scripts are under this folder: `%AppData%\SpaceEngineers\IngameScripts\local`

Use the [In-game Script Merge Tool](https://github.com/viktor-ferenczi/se-script-merge)
for in-game script development in proper IDE. Allows
merging script from multiple files, sharing code between scripts,
introducing unit tests not copied into script and minifying
script for release.

## Remarks

- This plugin designed solely for local script development.
- Works only in offline and locally hosted games.
- Not scalable to large number of PBs.
