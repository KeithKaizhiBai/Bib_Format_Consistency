# -*- coding: utf-8 -*-
"""
Normalize @article entries in a BibTeX file to PRL-style format.
Keeps citation keys unchanged; only normalizes @article entries.
"""

import re
import sys
from pathlib import Path

# Journal name to standard abbreviation (APS, AIP, etc.)
JOURNAL_ABBREV = {
    "physical review letters": "Phys. Rev. Lett.",
    "phys. rev. lett.": "Phys. Rev. Lett.",
    "physical review b": "Phys. Rev. B",
    "phys. rev. b": "Phys. Rev. B",
    "physical review a": "Phys. Rev. A",
    "phys. rev. a": "Phys. Rev. A",
    "physical review x": "Phys. Rev. X",
    "phys. rev. x": "Phys. Rev. X",
    "physical review d": "Phys. Rev. D",
    "phys. rev. d": "Phys. Rev. D",
    "physical review": "Phys. Rev.",
    "phys. rev.": "Phys. Rev.",
    "physical review research": "Phys. Rev. Res.",
    "phys. rev. res.": "Phys. Rev. Res.",
    "physical review applied": "Phys. Rev. Appl.",
    "phys. rev. appl.": "Phys. Rev. Appl.",
    "review of modern physics": "Rev. Mod. Phys.",
    "rev. mod. phys.": "Rev. Mod. Phys.",
    "reviews of modern physics": "Rev. Mod. Phys.",
    "nature": "Nature",
    "science": "Science",
    "applied physics letters": "Appl. Phys. Lett.",
    "appl. phys. lett.": "Appl. Phys. Lett.",
    "annual review of condensed matter physics": "Annu. Rev. Condens. Matter Phys.",
    "annu. rev. condens. matter phys.": "Annu. Rev. Condens. Matter Phys.",
    "annual review of condensed matter physics,": "Annu. Rev. Condens. Matter Phys.",
    "nature physics": "Nat. Phys.",
    "nat. phys.": "Nat. Phys.",
    "nature materials": "Nat. Mater.",
    "nat. mater.": "Nat. Mater.",
    "nature communications": "Nat. Commun.",
    "nat. commun.": "Nat. Commun.",
    "nat. communi.": "Nat. Commun.",
    "nature reviews materials": "Nat. Rev. Mater.",
    "science advances": "Sci. Adv.",
    "sci. adv.": "Sci. Adv.",
    "sci adv": "Sci. Adv.",
    "new journal of physics": "New J. Phys.",
    "new j. phys.": "New J. Phys.",
    "new j. phys": "New J. Phys.",
    "annals of physics": "Ann. Phys.",
    "ann. phys.": "Ann. Phys.",
    "proceedings of the national academy of sciences": "Proc. Natl. Acad. Sci. U.S.A.",
    "proc. natl. acad. sci. u.s.a.": "Proc. Natl. Acad. Sci. U.S.A.",
    "proc. natl. acad. sci.": "Proc. Natl. Acad. Sci. U.S.A.",
    "proceedings of the national academy of sciences of the united states of america": "Proc. Natl. Acad. Sci. U.S.A.",
    "solid state communications": "Solid State Commun.",
    "solid state commun.": "Solid State Commun.",
    "journal of applied physics": "J. Appl. Phys.",
    "j. appl. phys.": "J. Appl. Phys.",
    "journal of the physical society of japan": "J. Phys. Soc. Jpn.",
    "j. phys. soc. jpn.": "J. Phys. Soc. Jpn.",
    "physics reports": "Phys. Rep.",
    "phys. rep.": "Phys. Rep.",
    "communications physics": "Commun. Phys.",
    "commun. phys.": "Commun. Phys.",
    "scipost physics": "SciPost Phys.",
    "scipost phys.": "SciPost Phys.",
    "scipost phys. lect. notes": "SciPost Phys. Lect. Notes",
    "npj quantum materials": "npj Quantum Mater.",
    "npj quantum mater.": "npj Quantum Mater.",
    "chinese physics letters": "Chin. Phys. Lett.",
    "chin. phys. lett.": "Chin. Phys. Lett.",
    "national science review": "Nat. Sci. Rev.",
    "nat. sci. rev.": "Nat. Sci. Rev.",
    "apl materials": "APL Mater.",
    "apl mater.": "APL Mater.",
    "science china physics, mechanics & astronomy": "Sci. China Phys. Mech. Astron.",
    "science china physics, mechanics {\\&} astronomy": "Sci. China Phys. Mech. Astron.",
    "frontiers of physics": "Front. Phys.",
    "front. phys.": "Front. Phys.",
    "2d materials": "2D Mater.",
    "2d mater.": "2D Mater.",
    "advanced materials": "Adv. Mater.",
    "adv. mater.": "Adv. Mater.",
    "superconductor science and technology": "Supercond. Sci. Technol.",
    "supercond. sci. technol.": "Supercond. Sci. Technol.",
    "chemistry of materials": "Chem. Mater.",
    "chem. mater.": "Chem. Mater.",
    "transactions of the american mathematical society": "Trans. Am. Math. Soc.",
    "trans. am. math. soc.": "Trans. Am. Math. Soc.",
    "physics-uspekhi": "Phys.-Usp.",
    "physics uspekhi": "Phys.-Usp.",
    "soviet physics jetp": "Sov. Phys. JETP",
    "sov. phys. jetp": "Sov. Phys. JETP",
    "journal of applied crystallography": "J. Appl. Crystallogr.",
    "j. appl. crystallogr.": "J. Appl. Crystallogr.",
    "aip conference proceedings": "AIP Conf. Proc.",
    "crystengcomm": "CrystEngComm",
    "international tables for crystallography volume d: physical properties of crystals": "Int. Tables Crystallogr. D",
    "jourenal club of condensed matter physics": "J. Club Condens. Matter Phys.",
    "journal club of condensed matter physics": "J. Club Condens. Matter Phys.",
    # Additional journal abbreviations
    "nature nanotechnology": "Nat. Nanotechnol.",
    "nat. nanotechnol.": "Nat. Nanotechnol.",
    "american journal of mathematics": "Am. J. Math.",
    "am. j. math.": "Am. J. Math.",
    "journal of physics and chemistry of solids": "J. Phys. Chem. Solids",
    "j. phys. chem. solids": "J. Phys. Chem. Solids",
    "europhysics letters": "Europhys. Lett.",
    "europhys. lett.": "Europhys. Lett.",
    "reports on progress in physics": "Rep. Prog. Phys.",
    "rep. prog. phys.": "Rep. Prog. Phys.",
    "philosophical transactions of the royal society of london, series a: mathematical and physical sciences": "Philos. Trans. R. Soc. London A",
    "philos. trans. r. soc. london a": "Philos. Trans. R. Soc. London A",
    "proc. r. soc. lond. a": "Proc. R. Soc. London A",
    "european journal of physics": "Eur. J. Phys.",
    "eur. j. phys.": "Eur. J. Phys.",
    "advances in physics": "Adv. Phys.",
    "adv. phys.": "Adv. Phys.",
    "applied physics letters": "Appl. Phys. Lett.",
    "nature materials": "Nat. Mater.",
    "nano letters": "Nano Lett.",
    "nano lett.": "Nano Lett.",
    "scientific reports": "Sci. Rep.",
    "sci. rep.": "Sci. Rep.",
    "science bulletin": "Sci. Bull.",
    "sci. bull.": "Sci. Bull.",
    "physical review letters": "Phys. Rev. Lett.",
    "physical review b": "Phys. Rev. B",
    "nature reviews physics": "Nat. Rev. Phys.",
    "nat. rev. phys.": "Nat. Rev. Phys.",
    "nuclear physics b": "Nucl. Phys. B",
    "nucl. phys. b": "Nucl. Phys. B",
    "npj quantum information": "npj Quantum Inf.",
    "npj quantum inf.": "npj Quantum Inf.",
    "national science review": "Nat. Sci. Rev.",
    "physics letters b": "Phys. Lett. B",
    "phys. lett. b": "Phys. Lett. B",
    "low temperature physics": "Low Temp. Phys.",
    "low temp. phys.": "Low Temp. Phys.",
    "the innovation": "The Innovation",
    "coshare science": "Coshare Sci.",
    "topology": "Topology",
    "the london, edinburgh, and dublin philosophical magazine and journal of science": "Philos. Mag.",
    "philosophical magazine": "Philos. Mag.",
    "philos. mag.": "Philos. Mag.",
}

# Surname prefixes (compound surnames)
VON_PREFIXES = frozenset("von van der de da di del la le".split())

# Month to abbreviation
MONTH_MAP = {
    "1": "Jan", "01": "Jan", "january": "Jan", "jan": "Jan",
    "2": "Feb", "02": "Feb", "february": "Feb", "feb": "Feb",
    "3": "Mar", "03": "Mar", "march": "Mar", "mar": "Mar",
    "4": "Apr", "04": "Apr", "april": "Apr", "apr": "Apr",
    "5": "May", "05": "May", "may": "May",
    "6": "Jun", "06": "Jun", "june": "Jun", "jun": "Jun",
    "7": "Jul", "07": "Jul", "july": "Jul", "jul": "Jul",
    "8": "Aug", "08": "Aug", "august": "Aug", "aug": "Aug",
    "9": "Sep", "09": "Sep", "september": "Sep", "sep": "Sep", "sept": "Sep",
    "10": "Oct", "october": "Oct", "oct": "Oct",
    "11": "Nov", "november": "Nov", "nov": "Nov",
    "12": "Dec", "december": "Dec", "dec": "Dec",
}

# Words not capitalized in title case (except first/last and after : or ?)
SMALL_WORDS = frozenset(
    "a an the and or but in on at to for of with by as from is was are were been be have has had do does did will would could should may might must can".split()
)

# Proper nouns / adjectives in titles: force first letter uppercase via $\mathrm{X}$rest
NAME_FORCE_MATH = frozenset(
    "dirac berry hall fermi abelian majorana weyl landau aharonov anandan chern bohr jones"
    "klein gordon heisenberg schrodinger pauli bragg wigner yang mills maxwell newton neumann"
    "lagrangian hamiltonian euler bernoulli cauchy riemann gauss schwinger clifford andreev"
    "stoner wohlfarth van waals brillouin".split()
)


def _is_force_math_name(core_lower):
    """True if word is a known name (or possessive like Berry's) that may need $\\mathrm{X}$rest."""
    if core_lower in NAME_FORCE_MATH:
        return True
    return any(core_lower.startswith(name + "'") for name in NAME_FORCE_MATH)


def strip_braces(s):
    """Remove outer braces from a BibTeX value, unify quotes."""
    if not s:
        return s
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1].strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1].strip()
    return s


def strip_plain_braces(s):
    """
    Remove one level of outer braces only if they are plain grouping (no LaTeX inside).
    Used for author names like {Okazaki} -> Okazaki; preserves {\'e} or {\"u} etc.
    """
    if not s or not s.strip():
        return s
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        inner = s[1:-1].strip()
        # Do not strip if content looks like LaTeX (backslash, or protected group)
        if '\\' not in inner and not (inner.startswith("'") or inner.startswith('"') or inner.startswith('`')):
            return inner
    return s


def strip_all_plain_braces(s):
    """
    Repeatedly remove plain brace groups until none left.
    E.g. Louis {H.} -> Louis H.; {Kauffman} -> Kauffman; preserves {\'e}.
    """
    if not s or '\\' in s:
        return s
    prev = None
    while prev != s:
        prev = s
        # Replace plain {x} with x (x has no backslash, no inner braces we need to protect)
        s = re.sub(r'\{([^{}\\]+)\}', r'\1', s)
    return s.strip()


def split_at_depth_zero(s, sep):
    """Split string by sep only when brace depth is 0."""
    parts = []
    depth = 0
    start = 0
    for i, c in enumerate(s):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif depth == 0 and s[i:i + len(sep)] == sep:
            parts.append(s[start:i].strip())
            start = i + len(sep)
    parts.append(s[start:].strip())
    return parts


def normalize_author(author_str):
    """
    Normalize author to "Last, First" format, multiple authors with " and ".
    Preserve LaTeX (\\o{}, {\\'e}, etc.) and name abbreviations.
    """
    if not author_str or not author_str.strip():
        return author_str
    raw = author_str.strip()
    # Normalize newlines and multiple spaces to single space, then split by " and "
    raw = re.sub(r'\s+', ' ', raw)
    parts = re.split(r'\s+and\s+', raw, flags=re.IGNORECASE)
    result = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Already "Last, First" format: contains exactly one comma not inside braces
        depth = 0
        comma_pos = -1
        for i, c in enumerate(p):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            elif c == ',' and depth == 0:
                comma_pos = i
                break
        if comma_pos > 0:
            last = strip_all_plain_braces(strip_plain_braces(p[:comma_pos].strip()))
            first = strip_all_plain_braces(strip_plain_braces(p[comma_pos + 1:].strip()))
            result.append(f"{last}, {first}")
            continue
        # "First Last" format: convert to "Last, First"
        # Split by space only at depth 0 so "Louis {H. Kauffman}" -> ["Louis", "{H. Kauffman}"]
        tokens = split_at_depth_zero(p, " ")
        tokens = [strip_all_plain_braces(strip_plain_braces(t)) for t in tokens if t]
        if not tokens:
            continue
        if len(tokens) == 1:
            result.append(tokens[0])
            continue
        # If last token is a von prefix, take last two as surname
        if tokens[-1].lower() in VON_PREFIXES and len(tokens) >= 2:
            surname = tokens[-2] + " " + tokens[-1]
            given = " ".join(tokens[:-2])
        else:
            # Last token might be "H. Kauffman" (initial + surname); want surname=Kauffman, given=Louis H.
            last_tok = tokens[-1]
            sub = last_tok.split()
            if len(sub) >= 2 and sub[0].endswith('.') and len(sub[0]) <= 3:
                # e.g. "H." or "J." then "Kauffman"
                surname = sub[-1]
                given = " ".join(tokens[:-1] + sub[:-1])
            else:
                surname = last_tok
                given = " ".join(tokens[:-1])
        if given:
            result.append(f"{surname}, {given}")
        else:
            result.append(surname)
    return " and ".join(result)


def normalize_journal(journal_str):
    """Return standard journal abbreviation."""
    if not journal_str:
        return journal_str
    j = strip_braces(journal_str).strip()
    key = j.lower().replace("&", " and ")
    return JOURNAL_ABBREV.get(key, j)


def title_case_word(word, after_colon_or_question=False):
    """Capitalize word for title case; preserve LaTeX and math."""
    if not word:
        return word
    # Don't change if it contains LaTeX/math (e.g. $...$, \mathrm, etc.)
    if '\\' in word or '$' in word or word.startswith('{'):
        return word
    if after_colon_or_question or word.lower() not in SMALL_WORDS:
        return word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper()
    return word.lower()


def normalize_title(title_str):
    """Apply title case; preserve LaTeX and math; capitalize after : or ?"""
    if not title_str:
        return title_str
    t = strip_braces(title_str)
    # Simple title case: split by spaces, capitalize first of each word (and after :/?)
    out = []
    cap_next = True
    for i, w in enumerate(re.split(r'(\s+)', t)):
        if not w.strip():
            out.append(w)
            continue
        if w.strip() in ':?':
            out.append(w)
            cap_next = True
            continue
        if w.strip().endswith(':') or w.strip().endswith('?'):
            cap_next = True
        if re.match(r'^\s+$', w):
            out.append(w)
            continue
        # Protect LaTeX/math segments entirely (e.g. $\mathbb{Z}_2$, \mathrm, etc.)
        if '\\' in w or '$' in w:
            out.append(w)
            # After LaTeX/math, keep current cap_next logic based on punctuation only
            cap_next = (w.strip().endswith(':') or w.strip().endswith('?'))
            continue

        w_orig = w  # keep original for "only force when source was lowercase" check
        # Find first alphabetic character position (to handle leading braces, quotes, etc.)
        alpha_idx = None
        for idx, ch in enumerate(w):
            if ch.isalpha():
                alpha_idx = idx
                break

        if alpha_idx is not None:
            # Decide whether this word should be capitalized or lowercased
            should_cap = cap_next or w.strip().lower() not in SMALL_WORDS
            ch = w[alpha_idx]
            if should_cap:
                w = w[:alpha_idx] + ch.upper() + w[alpha_idx + 1:]
            else:
                w = w[:alpha_idx] + ch.lower() + w[alpha_idx + 1:]
            # Force first letter via $\mathrm{X}$rest: possessive always; non-first-word always; first word skip (no redundant format)
            core_lower = w.strip().strip('{}').lower()
            need_force = _is_force_math_name(core_lower) and ("'" in core_lower or not cap_next)
            if need_force:
                w = w[:alpha_idx] + "$\\mathrm{" + w[alpha_idx].upper() + "}$" + w[alpha_idx + 1:]
            if "-" in w and not need_force:
                # Hyphenated: e.g. Non-Abelian -> Non-$\mathrm{A}$belian
                subparts = w.split("-")
                new_parts = []
                for j, part in enumerate(subparts):
                    pl = part.strip().strip('{}').lower()
                    idx_first = next((k for k, c in enumerate(part) if c.isalpha()), None)
                    if pl in NAME_FORCE_MATH and idx_first is not None:
                        part = part[:idx_first] + "$\\mathrm{" + part[idx_first].upper() + "}$" + part[idx_first + 1:]
                    new_parts.append(part)
                w = "-".join(new_parts)
        out.append(w)
        # After colon/question, next word should be capitalized; do not reset cap_next
        cap_next = (w.strip().endswith(':') or w.strip().endswith('?'))
    result = "".join(out)
    result = _format_chemical_formulas_in_title(result)
    return result


def _format_chemical_formulas_in_title(title):
    """
    In plain-text segments (outside $...$), convert chemical formulas like Bi_2Se_3 or MnBi2Te4
    to $\\mathrm{Bi}_2\\mathrm{Se}_3$ so element symbols are forced uppercase.
    """
    # Split by $ so we only modify text outside math
    parts = re.split(r'(\$[^$]*\$)', title)
    out = []
    for i, seg in enumerate(parts):
        if seg.startswith('$') and seg.endswith('$'):
            out.append(seg)
            continue
        # In plain text: find runs of element(s)+subscript(s), min length 3 to avoid single letters
        def replace_formula(m):
            run = m.group(0)
            if len(run) < 3:
                return run
            # Break into (Element)(subscript)*; element = [A-Z][a-z]?, subscript = _\d+ or \d+
            tokens = re.findall(r'([A-Z][a-z]?)((?:_\d+|\d+)*)', run)
            if not tokens:
                return run
            s = []
            for elem, sub in tokens:
                s.append("\\mathrm{" + elem + "}")
                if sub:
                    s.append("_" + sub.replace("_", ""))
            return "$" + "".join(s) + "$"
        seg = re.sub(r'(?:[A-Z][a-z]?(?:_\d+|\d+)*)+', replace_formula, seg)
        out.append(seg)
    return "".join(out)


def normalize_pages(pages_str):
    """Use double hyphen for page ranges."""
    if not pages_str:
        return pages_str
    p = strip_braces(pages_str).strip()
    # Replace single hyphen between two numbers with double hyphen
    p = re.sub(r'(\d)\s*-\s*(\d)', r'\1--\2', p)
    return p


def normalize_month(month_str):
    """Month to English abbreviation."""
    if not month_str:
        return month_str
    m = strip_braces(month_str).strip().lower()
    return MONTH_MAP.get(m, month_str if len(month_str) <= 4 else month_str[:3].capitalize())


def normalize_year(year_str):
    """Ensure 4-digit year."""
    if not year_str:
        return year_str
    y = strip_braces(year_str).strip()
    try:
        yi = int(y)
        if yi < 100:
            return str(1900 + yi) if yi >= 50 else str(2000 + yi)
        return str(yi)
    except ValueError:
        return y


def normalize_doi(doi_str):
    """Ensure DOI is just the identifier (e.g. 10.1103/...)."""
    if not doi_str:
        return doi_str
    d = strip_braces(doi_str).strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/"):
        if d.lower().startswith(prefix):
            d = d[len(prefix):]
            break
    return d


def normalize_url(url_str):
    """Ensure URL starts with https://."""
    if not url_str:
        return url_str
    u = strip_braces(url_str).strip()
    if u.startswith("http://"):
        u = "https://" + u[7:]
    elif not u.startswith("https://"):
        if u.startswith("doi.org/"):
            u = "https://" + u
        elif u.startswith("dx.doi.org/"):
            u = "https://" + u.replace("dx.doi.org", "doi.org")
        else:
            u = "https://" + u
    return u


def _entry_fields(entry):
    """Return dict of fields (bibtexparser v1: flat with ID/ENTRYTYPE; v2: entry['fields'])."""
    if "fields" in entry:
        return dict(entry["fields"])
    return {k: v for k, v in entry.items() if k not in ("ID", "ENTRYTYPE", "key", "type")}


def _entry_key(entry):
    return entry.get("ID") or entry.get("key", "")


def get_field(entry, key, alt_keys=None):
    """Get field value; key is case-insensitive; try alt_keys if key missing."""
    fields = _entry_fields(entry)
    key_lower = key.lower()
    for k, v in fields.items():
        if k.lower() == key_lower:
            return v
    for alt in (alt_keys or []):
        for k, v in fields.items():
            if k.lower() == alt.lower():
                return v
    return None


def set_field(fields, key, value):
    """Set field, removing old key if different case."""
    to_remove = [k for k in fields if k.lower() == key.lower()]
    for k in to_remove:
        del fields[k]
    if value is not None and value != "":
        fields[key] = value


def format_entry_prl(entry):
    """Format a single @article entry in PRL style."""
    fields = _entry_fields(entry)
    key = _entry_key(entry)

    # Normalize fields (only for existing values)
    author = get_field(entry, "author")
    if author:
        set_field(fields, "author", normalize_author(author))

    journal = get_field(entry, "journal")
    if journal:
        set_field(fields, "journal", normalize_journal(journal))

    title = get_field(entry, "title")
    if title:
        set_field(fields, "title", normalize_title(title))

    pages = get_field(entry, "pages")
    if pages:
        set_field(fields, "pages", normalize_pages(pages))

    # issue: prefer 'issue', then 'number'
    issue = get_field(entry, "issue") or get_field(entry, "number")
    if issue:
        # If number looks like "Volume 6, 2015" or "5", keep numeric part only
        issue_clean = strip_braces(issue).strip()
        if issue_clean.lower().startswith("volume"):
            match = re.search(r"(\d+)", issue_clean)
            if match:
                issue_clean = match.group(1)
        set_field(fields, "issue", issue_clean)
        if "number" in fields:
            del fields["number"]

    month = get_field(entry, "month")
    if month:
        set_field(fields, "month", normalize_month(month))

    year = get_field(entry, "year")
    if year:
        set_field(fields, "year", normalize_year(year))

    doi = get_field(entry, "doi")
    if doi:
        set_field(fields, "doi", normalize_doi(doi))

    url = get_field(entry, "url") or get_field(entry, "URL")
    if url:
        set_field(fields, "url", normalize_url(url))
    elif doi:
        set_field(fields, "url", "https://doi.org/" + doi)
    if "URL" in fields:
        del fields["URL"]

    # Use article-number as pages when pages is missing (e.g. Nat. Commun. article IDs)
    if not get_field(entry, "pages") and get_field(entry, "article-number"):
        artnum = strip_braces(get_field(entry, "article-number")).strip()
        set_field(fields, "pages", artnum)
    if "article-number" in fields:
        del fields["article-number"]

    # Infer missing volume/pages from DOI for consistent bibliography output (e.g. ACS Nano Lett.)
    journal_lower = (journal or "").lower()
    if doi and not get_field(entry, "pages"):
        m = re.search(r"10\.1021/acs\.nanolett\.([\w\-]+)", doi)
        if m:
            set_field(fields, "pages", m.group(1))
    if not get_field(entry, "volume") and doi:
        year_str = get_field(entry, "year") or ""
        year_str = strip_braces(year_str).strip()
        try:
            y = int(year_str)
            if 2000 <= y <= 2030 and ("nano lett" in journal_lower or "nanolett" in (doi or "")):
                set_field(fields, "volume", str(y % 100 if y >= 2000 else y))
        except ValueError:
            pass

    # Strict field order so every article matches the same format (e.g. hsieh2012topological).
    # Core first, then standard optional, then trailing extras in fixed order.
    canonical_order = [
        "title", "author", "journal", "volume", "issue", "pages", "numpages",
        "year", "month", "publisher", "doi", "url", "issn", "abstract", "day"
    ]
    trailing_order = [
        "eissn", "eprint", "date-added", "date-modified", "bdsk-url-1", "bdsk-url-2",
        "urldate", "isbn", "adsurl", "adsnote", "unique-id", "orcid-numbers",
        "researcherid-numbers", "keywords", "type", "note"
    ]
    ordered = []
    seen = set()
    for k in canonical_order:
        if k in fields:
            ordered.append((k, fields[k]))
            seen.add(k.lower())
    for k in trailing_order:
        if k in fields:
            ordered.append((k, fields[k]))
            seen.add(k.lower())
    for k, v in sorted(fields.items(), key=lambda x: x[0].lower()):
        if k.lower() not in seen:
            ordered.append((k, v))

    lines = ["@article{" + key + ","]
    for i, (k, v) in enumerate(ordered):
        # BibTeX value: always wrap in exactly one outer pair of braces so the
        # value is a single brace-delimited block. Otherwise a value like
        # {${\mathbb Z}_2$} Rest... is parsed as only ${\mathbb Z}_2$ (first }
        # closes the value).
        if isinstance(v, str):
            val = v.strip()
        else:
            val = str(v)
        val = "{" + val + "}"
        comma = "," if i < len(ordered) - 1 else ""
        lines.append(f"  {k} = {val}{comma}")
    lines.append("}")
    return "\n".join(lines)


def format_entry_title_only(entry):
    """Format any entry type with only title normalized. Uses the same normalize_title() as
    article (including first-word exception and name $\\mathrm{X}$rest), so title rules
    apply uniformly to inbook, book, incollection, etc."""
    etype = entry.get("ENTRYTYPE") or entry.get("type", "misc")
    key = _entry_key(entry)
    fields = _entry_fields(entry)
    title = get_field(entry, "title")
    if title:
        set_field(fields, "title", normalize_title(title))
    # Output: title first if present, then rest alphabetically
    order_keys = ["title"] + sorted([k for k in fields if k.lower() != "title"], key=lambda x: x.lower())
    ordered = [(k, fields[k]) for k in order_keys if k in fields]
    lines = ["@" + etype + "{" + key + ","]
    for i, (k, v) in enumerate(ordered):
        val = (v.strip() if isinstance(v, str) else str(v))
        val = "{" + val + "}"
        comma = "," if i < len(ordered) - 1 else ""
        lines.append(f"  {k} = {val}{comma}")
    lines.append("}")
    return "\n".join(lines)


def split_bib_entries(content):
    """Split bib file content into list of (entry_type, key, raw_block)."""
    entries = []
    i = 0
    while i < len(content):
        # Find next @type{key
        m = re.search(r'@(\w+)\s*\{([^,\s]+)\s*,', content[i:], re.IGNORECASE)
        if not m:
            break
        start = i + m.start()
        i = i + m.end()
        entry_type = m.group(1)
        key = m.group(2)
        # Find matching closing brace: the { that opens after @type is at start + position of {
        brace_start = start + content[start:].find('{')
        depth = 1
        pos = brace_start + 1
        while pos < len(content) and depth > 0:
            c = content[pos]
            if c == '{' and (pos == 0 or content[pos-1] != '\\'):
                depth += 1
            elif c == '}' and (pos == 0 or content[pos-1] != '\\'):
                depth -= 1
            pos += 1
        raw_block = content[start:pos].strip()
        entries.append((entry_type, key, raw_block))
        i = pos
    return entries


def parse_single_entry(raw_block):
    """Parse a single BibTeX entry string into bibtexparser entry dict."""
    try:
        import bibtexparser
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bibtexparser", "-q"])
        import bibtexparser
    # Support both v1 (loads) and v2 (parse_string)
    if hasattr(bibtexparser, 'parse_string'):
        parser = bibtexparser.bparser.BibTexParser(common_strings=True) if hasattr(bibtexparser, 'bparser') else None
        db = bibtexparser.parse_string(raw_block + "\n", parser) if parser else bibtexparser.parse_string(raw_block + "\n")
    else:
        db = bibtexparser.loads(raw_block + "\n")
    if not db.entries:
        return None
    return db.entries[0]


def parse_bib_file(path):
    """Parse .bib file and return list of entries (preserving order)."""
    try:
        import bibtexparser
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bibtexparser", "-q"])
        import bibtexparser
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    db = bibtexparser.loads(content) if not hasattr(bibtexparser, 'parse_string') else bibtexparser.parse_string(content)
    return db.entries


def write_bib_file_from_raw(content, out_path):
    """
    Split content into entries. For @article: full PRL normalization (includes title).
    For any other type (inbook, book, incollection, etc.): same title normalization rules
    (normalize_title, including first-word exception and name $\\mathrm{X}$rest) when the
    entry has a title; only the title field is normalized, rest preserved.
    """
    entries = split_bib_entries(content)
    output = []
    for entry_type, key, raw_block in entries:
        if entry_type.lower() == "article":
            parsed = parse_single_entry(raw_block)
            if parsed:
                output.append(format_entry_prl(parsed))
            else:
                output.append(raw_block)
        else:
            parsed = parse_single_entry(raw_block)
            if parsed and get_field(parsed, "title") is not None:
                output.append(format_entry_title_only(parsed))
            else:
                output.append(raw_block)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(output))
        f.write("\n")


def main():
    base = Path(__file__).resolve().parent
    src = base / "citations.bib"
    dst = base / "citations_norm.bib"
    if not src.exists():
        print(f"File not found: {src}", file=sys.stderr)
        sys.exit(1)
    with open(src, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    entries = split_bib_entries(content)
    print(f"Found {len(entries)} entries.", file=sys.stderr)
    write_bib_file_from_raw(content, dst)
    print(f"Written: {dst}", file=sys.stderr)


if __name__ == "__main__":
    main()
