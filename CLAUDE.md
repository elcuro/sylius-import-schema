# CLAUDE.md — sylius-import-schema

This file gives Claude context when working in this repository.

---

## What this repo is

An open XML schema for importing products into [Sylius](https://sylius.com/) e-commerce.
The schema is source-agnostic — it works for:

- **External suppliers** (ERP, BigBuy, partner systems) who do not know our internal Sylius codes
- **Sylius → Sylius** transfer between two Sylius instances

The schema is hosted on GitHub Pages so suppliers can reference the XSD directly in their XML files.

---

## Repo structure

```
sylius-import-schema/
├── CLAUDE.md                          ← you are here
├── README.md                          ← supplier-facing documentation
├── sylius-import-2.0.xsd              ← XSD schema (single source of truth)
├── examples/
│   ├── example-external.xml           ← external supplier example
│   ├── example-sylius.xml             ← Sylius to Sylius example
│   └── example-manifest.xml           ← multi-file manifest example
└── tests/
    ├── test-3.xml                     ← 3 products (smoke test)
    ├── test-50.xml                    ← 50 products
    ├── test-100.xml                   ← 100 products
    ├── test-500.xml                   ← 500 products (single file)
    ├── test-500-part-a.xml            ← 250 products (chunk A)
    ├── test-500-part-b.xml            ← 250 products (chunk B)
    └── test-500-manifest.xml          ← manifest referencing part-a + part-b
```

Test files are **generated** — do not edit them manually. Re-generate using:

```bash
python3 generate_test_xml.py
```

---

## Key design decisions

### Two import modes

| Mode | Root element | When to use |
|---|---|---|
| Single file | `<sylius-import>` | up to ~5,000 products |
| Multi-file | `<sylius-import-manifest>` + multiple `<sylius-import>` files | 5,000+ products |

### No dialect attribute

There is no `dialect="external|sylius"` attribute. Instead, the importer reads what is present:

- `code` present → used directly as the Sylius code
- `name` without `code` → mapped via importer configuration
- `external-code` → stored for future mapping

This means a single XML file can mix both approaches within the same document.

### Codes

Every element that has an identity supports three code fields:

| Attribute | Meaning |
|---|---|
| `code` | Our internal Sylius code |
| `external-code` | The supplier's internal code |
| `value-code` | Code for the value (select attributes, option values) |
| `external-value-code` | The supplier's code for the value |

### Prices

Always in the **smallest currency unit** (cents). `119900` = 1,199.00 EUR.
Never use decimal points in `amount`.

### Dimensions

Fixed units: `weight` in **kg**, `width` / `height` / `depth` in **mm**.

### Slugs

Slugs are **optional** in all translation elements.
The importer generates slugs from `name` when omitted.
Include slugs only when preserving them from a source Sylius instance.

### Content lives in child elements, not attributes

**All string/text content must be modelled as child elements**, never as
XML attributes. This applies to names, descriptions, codes, slugs,
values, URLs, paths — anything a supplier types or copy-pastes.

**Why:** XML attributes cannot contain `CDATA` blocks and force callers
to escape `<`, `>`, `&` and quotes. That breaks on realistic supplier
content like `Ben & Jerry's`, `L'Oréal`, HTML descriptions and URLs
with query strings (`?a=1&b=2`). Moving content to child elements lets
suppliers use `<![CDATA[ ... ]]>` and drop escaping entirely.

**How to apply:** when adding a new field to the XSD:

- If it is a free-form string (`xs:string`, `NonEmptyString`, `xs:anyURI`)
  → add it as a **child element** inside the complex type's `xs:sequence`.
- If it is a typed/constrained value (enum, integer, decimal, boolean,
  locale pattern, currency pattern) → it may stay as an **attribute**.
- Document-level metadata on the root (`version`, `default-locale`,
  `channel`) stays as attributes.
- References/selectors to a code elsewhere in the document (e.g.
  `<taxons main="...">`) may stay as attributes.

When in doubt: child element.

### default-locale

The `default-locale` attribute on `<sylius-import>` is a fallback.
Any `<translation>` without an explicit `locale` attribute inherits it.

---

## Validation

Always validate after editing any XML file:

```bash
# Single file
xmllint --schema sylius-import-2.0.xsd examples/example-external.xml --noout

# All files at once
for f in examples/*.xml tests/*.xml; do
  echo -n "$f: "
  xmllint --schema sylius-import-2.0.xsd "$f" --noout 2>&1
done
```

Expected output for every file: `filename validates`

---

## Environment policy — no host installs

Never install packages or tools on the host machine (no `apt install`,
`pip install`, `npm install -g`, `brew`, etc.). The host must stay clean.

If a tool is missing (xmllint, python packages, node tooling, ...), run it
inside a disposable container instead:

```bash
# Validate XML with xmllint inside an ephemeral container
docker run --rm -v "$PWD":/work -w /work alpine:latest \
    sh -c "apk add --no-cache libxml2-utils >/dev/null && \
           for f in examples/*.xml tests/*.xml; do \
               echo -n \"\$f: \"; xmllint --schema sylius-import-2.0.xsd \"\$f\" --noout; \
           done"

# Run Python with lxml / xmlschema inside a container
docker run --rm -v "$PWD":/work -w /work python:3.12-slim \
    sh -c "pip install --quiet lxml && python3 your-script.py"
```

If Docker itself is unavailable, ask the user before installing anything on
the host — do not `sudo apt-get install` on your own.

---

## Rules when editing the XSD

- All comments must be in **English**
- XML comments must **not contain `--`** (double hyphen) — it is invalid XML
- Every new element or attribute needs a comment explaining its purpose
- After any XSD change, re-validate all example and test files
- Bump `version` in the XSD header comment when making breaking changes
- Never remove existing elements — add new optional ones instead (backwards compatibility)
- **When adding a new field, default to a child element** (see *Content lives in child elements*). Only use an attribute for typed/enum/numeric values, references, or root metadata.
- **When adding any new element or attribute to the XSD, always update all of the following:**
  1. `examples/example-external.xml` — add a realistic value using the external-supplier style
  2. `examples/example-sylius.xml` — add a realistic value using the Sylius-to-Sylius style
  3. `README.md` — document the new field in the relevant section (table + example)
  4. `generate_test_xml.py` — include the new field in generated test data
  5. Re-run `python3 generate_test_xml.py` to regenerate `tests/`

---

## Rules when editing examples

- `examples/example-external.xml` — must use only `<name>`, `<value>`, `<external-code>`, `<external-value-code>` for options and attributes (no `<code>` / `<value-code>`)
- `examples/example-sylius.xml` — must use `<code>` and `<value-code>` throughout; `<slug>` must be present on all translations
- Both examples must include at least 2 products and 2 locales
- Both examples must include at least one CDATA block (e.g. in `<description>`) to exercise the "content in child elements" rule
- Both examples must validate against the XSD before committing

---

## Rules when editing test files

Test files in `tests/` are auto-generated by `generate_test_xml.py`.
Do **not** edit them manually — changes will be lost on the next run.

To change test data, edit `generate_test_xml.py` and re-run:

```bash
python3 generate_test_xml.py
```

Then validate:

```bash
for f in tests/*.xml; do
  echo -n "$f: "
  xmllint --schema sylius-import-2.0.xsd "$f" --noout 2>&1
done
```

---

## Planned / not yet implemented

- `<taxons>` definition block at the file level (currently taxons must pre-exist in Sylius)
- `<attributes>` definition block at the file level (same)
- `<options>` definition block at the file level (same)
- Delta / partial update mode (currently every import is a full upsert)
- Image download from URL (currently handled by the importer, not the schema)
- Tier pricing / customer group pricing
- Associations (upsell, crosssell)
- Bundle products

---

## Related

- Sylius plugin that consumes this schema: `your-org/sylius-bigbuy-plugin` *(link when available)*
- BigBuy API docs: https://api.bigbuy.eu/rest/doc
