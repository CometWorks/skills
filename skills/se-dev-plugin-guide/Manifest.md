# Fill the manifest XML

The manifest tells the hub and Pulsar where your code is and how to build it. The template ships it in the
repository root, renamed by `setup.py` (the server template ships one for each hub). The same format serves
PluginHub and MagnetarHub; QuasarHub has its own.

```xml
<?xml version="1.0"?>
<PluginData xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="GitHubPlugin">
    <Id>3F2B9C1E-0D4A-4E57-9B8C-6A1F2E3D4C5B</Id>
    <RepoId>your-github-user/your-plugin</RepoId>
    <FriendlyName>Your Plugin</FriendlyName>
    <Author>Your Name</Author>
    <Tooltip>One line shown in the plugin list.</Tooltip>
    <Description>
        What the plugin does, how to use it and where to report bugs.

        Players can click links here, for example a Discord invite.
    </Description>
    <SourceDirectories>
        <Directory>ClientPlugin</Directory>
    </SourceDirectories>
    <Commit>0123456789abcdef0123456789abcdef01234567</Commit>
</PluginData>
```

| Element | Required | Meaning |
|---|---|---|
| `Id` | yes | Permanent identifier, a GUID from `setup.py`. Profiles and other plugins refer to it: never change it. Older plugins use `owner/repo` here. |
| `RepoId` | yes | The GitHub repository as `owner/repo`. Without it Pulsar uses `Id`. |
| `FriendlyName` | yes | Name in the plugin list. |
| `Author` | yes | Author shown in the list. |
| `Tooltip` | no | One-line summary in the list. |
| `Description` | no | Text of the details panel, up to 1000 characters. Indent it with the XML (the common indentation is removed), keep each paragraph on one line and separate paragraphs with a blank line. |
| `Commit` | yes | Full commit hash of the release, lowercase. Pulsar downloads and compiles exactly this commit. |
| `SourceDirectories` | no | Folders whose `.cs` files are compiled (case-sensitive). Without it every `.cs` file in the repository is compiled, test projects included. |
| `NuGetReferences` | no | `<PackageReference Include="Name" Version="1.2.3" />` for each package. Your `.csproj` references are not used. Packages must support `net48` or `netstandard2.0` for Legacy; use `netstandard2.0` to cover both flavors. Don't add Harmony. |
| `Asset` | no | Files to put on disk: `<Asset Name="AssetFolder" Path="ClientPlugin/Assets/" />` copies a folder from the repository and makes Pulsar call your plugin's `LoadAssets(string folder)`. `Url` downloads a file (give its `Sha256`), `Extract="true"` unpacks an archive, `Placement="Bin"` puts it next to the DLL, `Reference="true"` compiles against a downloaded DLL. |
| `DependencyIds` | no | `<Id>` of plugins or Workshop mods that are enabled together with yours. |
| `GroupId` | no | Plugins sharing it are mutually exclusive: enabling one disables the others. |
| `Runtimes` | no | Where the plugin may load: `CLR` (.NET Framework), `Mono` (Proton), `CoreCLR` (.NET 10), comma separated. Empty means everywhere. |
| `Platforms` | no | `Windows`, `Linux`, `Proton`, comma separated. Empty means everywhere. |
| `Hidden` | no | `true` hides the plugin from the list unless it is enabled or searched for. For dependency-only or abandoned plugins. |
| `AlternateVersions` | no | Extra `<Version>` entries with a `Name` and a `Commit` that players can pick, for test builds. |

Older templates and samples show an `<AssetFolder>` element, a NuGet `<Config>` element and
`NETFramework`/`NETCoreApp` runtime names. Current Pulsar ignores or doesn't match these; use the forms
above.

For a server plugin on MagnetarHub, `SourceDirectories` lists `ServerPlugin` and `Shared`. A QuasarHub
manifest names the project to build (`ProjectPath`), the `quasar-plugin.json` package manifest and the
supported Quasar versions; copy `quasar-hub.xml` from the Quasar template.
