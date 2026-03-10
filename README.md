# Normalize BibTeX to PRL Style

This Python script normalizes `@article` entries in a BibTeX file to a consistent format inspired by **Physical Review Letters (PRL)**. It preserves all citation keys. Non-article entries (e.g., `@inbook`, `@book`, `@incollection`) receive the same **title normalization** as articles; only `@article` gets full PRL-style field normalization.

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
- **Title normalization for all entry types** – `@article` gets full normalization; any other type that has a `title` field gets the same title rules applied (see section below), with other fields preserved.

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
- For non-article entries that have a `title` field, the script parses the entry, applies the same title normalization (see below), and writes the entry back with only the title changed; other fields and entry types are preserved.
- The final output is written with a blank line between entries.

---

## Title normalization (later additions)

The following rules apply to **all** entries that have a `title` field (`@article`, `@inbook`, `@book`, `@incollection`, etc.). They are implemented in `normalize_title()` and are kept separate from the original PRL-style feature set above.

### Proper nouns / names in titles

- **Name protection with `$\mathrm{X}$rest`**  
  For a fixed list of proper nouns and adjectives (e.g. Dirac, Berry, Hall, Fermi, Abelian, Lagrangian, Landau), the first letter is forced in the output as `$\mathrm{X}$rest` (e.g. `$\mathrm{D}$irac`, `$\mathrm{H}$all`) so that bibliography styles cannot lowercase it.
- **First-word exception**  
  If such a name is the **first word** of the title (or the first word after a colon or question mark), the script does **not** add `$\mathrm{X}$rest`, to avoid redundant formatting (e.g. “Berry Phase” stays as is).
- **Possessive and non–first words**  
  For possessives (e.g. “Berry's Phase”) and for names that are not the first word (e.g. “the Dirac equation”, “Quantum Hall Effect”), `$\mathrm{X}$rest` is always applied.
- **Hyphenated names**  
  For hyphenated words (e.g. “Non-Abelian”), the name part is formatted as above (e.g. “Non-$\mathrm{A}$belian”). The list of names is in `NAME_FORCE_MATH`; add or remove tokens there to change behavior.

### Chemical / material formulas in titles

- Plain-text chemical formulas (e.g. `Bi_2Se_3`, `MnBi2Te4`, `HgTe`) are detected and converted to math with upright element symbols, e.g. `$\mathrm{Bi}_2\mathrm{Se}_3$`, `$\mathrm{Mn}\mathrm{Bi}_2\mathrm{Te}_4$`, so that element capitalisation is preserved regardless of bibliography style. Existing math segments (`$...$`) are left unchanged.

### Summary

| Situation | Example | Output |
|-----------|--------|--------|
| Name as first word | Berry Phase Effects | Berry Phase Effects |
| Name not first word | the Dirac equation | the $\mathrm{D}$irac equation |
| Possessive | Berry's Phase | $\mathrm{B}$erry's Phase |
| Hyphenated | Non-Abelian | Non-$\mathrm{A}$belian |
| Chemical formula | MnBi2Te4 films | $\mathrm{Mn}\mathrm{Bi}_2\mathrm{Te}_4$ films |

---

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
- Non-article entries without a `title` field are copied verbatim. Non-article entries with a `title` have only the title normalized (same rules as above); other fields are preserved.

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