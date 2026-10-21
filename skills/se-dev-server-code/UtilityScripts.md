Catalog of utility scripts:

- `uv run search_server_code.py [options] <category> <symbol_type> <patterns...>` - Search code index (run with no args for full help)
- `uv run index_code.py <source_root_path> <output_directory>` - Rebuild code index
- `uv run check_index.py [--content] <CodeIndex>` - Report whether code (or content) index complete; exit 0 ok, 2 missing or broken. Preparation uses it to decide whether re-indexing needed
- `uv run index_content.py <content_dir> <decompiled_dir> <output_dir>` - Rebuild content index (`content_index.csv`)
- `hierarchy_tree.py` - Helper module for generating hierarchy tree text files (imported by indexer, not run directly)
- `uv run copy_content.py <ServerRoot>/Content` - Copy server content files into `Data/Content` (used by preparation script)
- `uv run check_version.py <Bin64> Data` (or `--print <Bin64>`, `--write <Bin64> Data`) - Detect server version label; compare it with `Data/game_version.txt`, print it, or record it there (used by preparation script)
- `uv run fix_case_collisions.py Data/Decompiled` - Move case-colliding namespace folders apart (used by preparation script)
- `uv run hash_server_files.py --write|--verify <ServerRoot> Data` - Record or verify SHA256 of every original server file (see [ServerFileHashes.md](ServerFileHashes.md))
- `./verify_server_files.sh` / `VerifyServerFiles.bat` - Verify installed server files against `Data/server_files.json`
