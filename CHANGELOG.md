# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this repository adheres to [Semantic Versioning](https://semver.org/).

## Two version numbers

Do not confuse them:

| What | Where it lives | Current | Bumps when |
|---|---|---|---|
| **Release version** | git tag, `VERSION` | `2.1.0` | every release, following SemVer |
| **Schema version** | `<sylius-import version="…">`, XSD file name, XSD header | `2.0` | **only** on a breaking change |

The MAJOR of the release version always equals the MAJOR of the schema
version. A breaking schema change means a MAJOR release, a new schema
version and a new XSD file (`sylius-import-3.0.xsd`); the previous file
stays online forever so documents already in the wild keep validating.

MINOR and PATCH releases never touch the schema version. Supplier XML
files keep declaring `version="2.0"` for the whole 2.x line.

## [2.1.0] - 2026-08-20

### Added

- Variant images, in two combinable forms:
  - `<variant><images>` — pictures owned by a single variant.
  - `<variants>` selector inside a product-level `<image>` — attaches one
    shared file to specific variants via `<variant-code>` (our Sylius code)
    or `<external-variant-code>` (the supplier's code); both may be mixed
    in one selector.
- New XSD types `VariantImagesType`, `VariantImageType` and
  `ImageVariantRefsType`.
- README section *Variant images* describing when to use which form and
  how the two are merged.
- Generated fixtures now cover both forms in every file, including a
  de-duplication case (every 10th product repeats the same URL through
  both mechanisms at once) so importers can verify they collapse it into
  a single image.

### Notes

- Purely additive; every document valid under 2.0.0 is still valid.
  The schema version therefore stays `2.0`.

## [2.0.0] - 2026-04-17

First tagged release. Baseline of the 2.0 schema line, covering everything
up to and including commit `7285956`.

### Added

- `<sylius-import>` and `<sylius-import-manifest>` root elements, products,
  translations, taxons, attributes, images, variants, options, price, stock
  and dimensions.
- Product `<manufacturer>` and `<brand>`; variant `<ean>`.
- Variant `condition` attribute (`new` / `used` / `refurbished`).
- VAT pricing on `<price>`: `vat-amount` and `vat` alongside `amount`.
- GPSR block (EU 2023/988): manufacturer identity, EU responsible person,
  model, safety notices, safety documents and certifications.
- Absolute `http(s)` URLs allowed in manifest `<file>` entries.
- `generate_test_xml.py` plus the generated fixtures in `tests/`, published
  over GitHub Pages.

### Changed

- All string content moved from XML attributes to child elements, so
  suppliers can use `CDATA` and stop escaping `&`, `<` and quotes.

### Notes

- The move of string content to child elements (`df15be0`) was a breaking
  change to the contract. It happened before this repository had any tags
  or releases, while the schema was still being introduced as 2.0, so it is
  folded into this baseline rather than treated as a MAJOR bump. From 2.0.0
  onwards every breaking change gets its own MAJOR release and its own XSD
  file.

[2.1.0]: https://github.com/elcuro/sylius-import-schema/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/elcuro/sylius-import-schema/releases/tag/v2.0.0
