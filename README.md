# Normalize BibTeX to PRL Style

This Python script normalizes `@article` entries in a BibTeX file to a consistent format inspired by **Physical Review Letters (PRL)**. It preserves all citation keys and leaves other entry types (e.g., `@book`, `@inproceedings`) untouched. Nevertheless, there are still some small bugs...

## Features

- **Author normalization** – converts to `Last, First` format while preserving LaTeX accents (`{\'e}`, `\o{}`, etc.) and initials.
- **Journal abbreviation** – maps common journal names to their standard abbreviations (e.g., *Physical Review Letters* → `Phys. Rev. Lett.`). The mapping can be extended by editing the `JOURNAL_ABBREV` dictionary.
- **Title case** – applies title capitalization (first and last words capitalized, small words lowercased) while protecting LaTeX math (`$...$`) and special commands.
- **Page ranges** – replaces single hyphens with double hyphens (`1-10` → `1--10`).
- **Month abbreviation** – converts month numbers/names to three‑letter abbreviations (Jan, Feb, …).
- **Year normalization** – ensures four‑digit years (e.g., `23` → `2023`).
- **DOI & URL cleaning** – strips DOI prefixes (`https://doi.org/`) and ensures URLs start with `https://`.
- **Field ordering** – arranges fields in a canonical order (title, author, journal, volume, issue, pages, year, month, publisher, doi, url, etc.) for a uniform appearance.
- **Fallback inference** – for certain journals (e.g., *Nano Letters*), attempts to guess missing volume/pages from the DOI.
- **Preserves non‑article entries** – only `@article` entries are processed; everything else is copied verbatim.

## Requirements

- Python 3.6 or higher
- [bibtexparser](https://github.com/sciunto-org/python-bibtexparser) – will be installed automatically if missing.

## Usage

1. Place the script (`normalize_bibtex.py`) in the same folder as your BibTeX file (default name: `citations.bib`).
2. Run from the terminal:
   ```bash
   python normalize_bibtex.py
   ```
3. The normalized output is written to `citations_norm.bib` in the same directory.

### Customizing Input/Output Files

To process a different file, modify the `src` and `dst` variables in the `main()` function:

```python
src = Path("/path/to/your/file.bib")
dst = Path("/path/to/output.bib")
```

## How It Works

- The script reads the entire BibTeX file, splits it into individual entries, and identifies each entry’s type.
- For `@article` entries, it parses the content using `bibtexparser`, normalizes each field according to the rules above, and rebuilds the entry with a fixed field order.
- All other entries are written back unchanged.
- The final output is written with a blank line between entries.

## Customization

### Adding Journal Abbreviations

Edit the `JOURNAL_ABBREV` dictionary in the script. Add entries in lowercase, e.g.:

```python
"new journal of physics": "New J. Phys.",
```

### Modifying Field Order

The canonical field order is defined in `canonical_order` and `trailing_order` inside `format_entry_prl()`. Adjust these lists to suit your preference.

## Important Notes

- **Always back up your original BibTeX file** before running the script, as the output overwrites any existing file with the same name.
- The script tries to preserve LaTeX markup, but it may not handle every exotic case perfectly. Always review the output, especially for titles and authors with complex formatting.
- Month conversion relies on a fixed mapping; if your file contains non‑standard month strings, they may be left unchanged.
- The automatic inference of volume/pages from DOI is heuristic and currently tailored for *Nano Letters* (`10.1021/acs.nanolett.XXXXX`). You can extend this logic in the code if needed.
- Entries that are not `@article` are copied verbatim, including any formatting issues they may have.

## Example

**Before** (a typical BibTeX entry):
```bibtex
@article{Muzaffar2025Switchable,
  title = {Ferroelectrically Switchable Half-Quantized Hall Effect},
  author = {Muzaffar, M. U. and Bai, Kai-Zhi and Qin, Wei and Cao, Guohua and Fu, Bo and Cui, Ping and Shen, Shun-Qing and Zhang, Zhenyu},
  journal = {Nano Lett.},
  year = {2025},
  month = {Apr},
  publisher = {American Chemical Society},
  doi = {10.1021/acs.nanolett.5c00550},
  url = {https://doi.org/10.1021/acs.nanolett.5c00550},
  eprint = {https://doi.org/10.1021/acs.nanolett.5c00550},
  note ={PMID: 40272043},
  issn = {1530-6984},
  day = {24}
}
```

**After** normalization:
```bibtex
@article{Muzaffar2025Switchable,
  title = {Ferroelectrically Switchable Half-Quantized Hall Effect},
  author = {Muzaffar, M. U. and Bai, Kai-Zhi and Qin, Wei and Cao, Guohua and Fu, Bo and Cui, Ping and Shen, Shun-Qing and Zhang, Zhenyu},
  journal = {Nano Lett.},
  year = {2025},
  doi = {10.1021/acs.nanolett.5c00550},
  url = {https://doi.org/10.1021/acs.nanolett.5c00550},
  eprint = {https://doi.org/10.1021/acs.nanolett.5c00550},
  note = {PMID: 40272043}
}
```

## License

This script is provided as‑is for academic use. Feel free to modify it to fit your own requirements.

---


For questions or suggestions, please contact the author or open an issue on the repository where this script was obtained.
