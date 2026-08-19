Catalog of utility scripts:

- `uv run search_game_code.py [options] <category> <symbol_type> <patterns...>` - Search code index (run with no args for full help)
- `uv run index_code.py <source_root_path> <output_directory>` - Rebuild code index
- `uv run check_index.py [--content] <CodeIndex>` - Report whether code (or content) index complete; exit 0 ok, 2 missing or broken. Preparation uses it to decide whether re-indexing needed
- `uv run hierarchy_tree.py` - Helper module for generating hierarchy tree text files (used by indexer)
- `uv run copy_content.py` - Copy game content files (used by preparation script)
- `uv run hash_game_files.py --write|--verify <GameRoot> Data` - Record or verify SHA256 of every original game file (see [GameFileHashes.md](GameFileHashes.md))
- `./verify_game_files.sh` / `VerifyGameFiles.bat` - Verify installed game files against `Data/game_files.json`
