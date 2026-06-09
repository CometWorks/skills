# Krafs Publicizer

## Enabling Publicizer

If your code needs to access internal, protected or private members, you likely want to enable Krafs publicizer in project to avoid writing reflections. Enable publicizer by uncommenting project file and C# code blocks marked with comments containing "Uncomment to enable publicizer support". Do not miss any of those.

## Synchronization

If you use Krafs publicizer, ensure `<Publicize>` entries in project file are ALWAYS in sync with `IgnoresAccessChecksTo` entries in C# code (`GameAssembliesToPublicize.cs` file).

## Handling Ambiguity Errors

If plugin's build process reports ambiguity errors on use of publicized symbols (typically events, but can be other symbols too), ignore those symbols from publicization by adding `<DoNotPublicize>` entry for each in project file.

## Documentation

Documentation of Krafs publicizer: https://github.com/krafs/Publicizer