# Sylius Import Schema — v2.0

This repository contains the XML schema for importing products into the Sylius e-commerce platform.

## Files

| File | Description |
|---|---|
| `sylius-import-2.0.xsd` | XSD schema — used to validate XML files before sending |
| `examples/example-external.xml` | Example for external suppliers (ERP, partner systems) |
| `examples/example-sylius.xml` | Example for Sylius to Sylius transfer |
| `examples/example-manifest.xml` | Example manifest for multi-file imports |

---

## Design rule — content in child elements

All string content (names, descriptions, codes, slugs, values, URLs, paths…)
lives in **child elements**, not attributes. Attributes are reserved for
typed tokens — enums, numbers, booleans, locale and currency patterns —
and document-level metadata (`version`, `default-locale`, `channel`).

This lets you safely include quotes, apostrophes, ampersands and HTML
without escaping — just wrap the content in a `CDATA` block:

```xml
<translation>
    <name>Ben &amp; Jerry's "Chunky Monkey"</name>
    <description><![CDATA[<p>HTML with <strong>tags</strong> & quotes.</p>]]></description>
</translation>
```

---

## Quick start

### 1. Choose the right approach

**Single file** (up to ~5,000 products):
→ send one `sylius-import` XML file directly

**Multiple files** (5,000+ products):
→ split into multiple `sylius-import` files and send a `sylius-import-manifest` alongside them

**Not sure which example to use?**

| | External supplier | Sylius to Sylius |
|---|---|---|
| You know our internal codes | no | yes |
| Use example | `example-external.xml` | `example-sylius.xml` |

### 2. Validate your XML before sending

```bash
# Install xmllint if you don't have it
# Ubuntu / Debian:
sudo apt install libxml2-utils

# macOS:
brew install libxml2

# Validate:
xmllint --schema sylius-import-2.0.xsd your-file.xml --noout

# Output if valid:
# your-file.xml validates

# Output if invalid:
# your-file.xml:47: element variant: Schemas validity error: ...
```

### 3. VS Code setup (optional)

Install the [XML extension by RedHat](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-xml).

Add the following to your root element to enable inline validation and autocomplete:

```xml
<sylius-import version="2.0"
               default-locale="en_US"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:noNamespaceSchemaLocation="https://elcuro.github.io/sylius-import-schema/sylius-import-2.0.xsd">
```

---

## XML structure

```
<sylius-import>
  <products>
    <product>
      <code/> <external-code/> <manufacturer/> <brand/>
      <translations>
        <translation>
          <name/> <slug/> <short-description/> <description/>
          <meta-title/> <meta-description/>
        </translation>
      </translations>
      <taxons>
        <taxon>
          <code/> <external-code/> <name/>
        </taxon>
      </taxons>
      <attributes>
        <attribute>
          <code/> <name/> <external-code/>
          <value/> <value-code/> <external-value-code/>
        </attribute>
      </attributes>
      <images>
        <image>
          <url/> <path/>
        </image>
      </images>
      <variants>
        <variant>
          <code/> <external-code/> <ean/>
          <translation>
            <name/> <slug/>
          </translation>
          <options>
            <option>
              <code/> <name/> <external-code/>
              <value/> <value-code/> <external-value-code/>
            </option>
          </options>
          <price />
          <stock />
          <dimensions />
        </variant>
      </variants>
      <gpsr>
        <manufacturer>
          <name/> <trademark/>
          <street/> <city/> <postal-code/> <country/>
          <email/> <phone/>
        </manufacturer>
        <eu-responsible-person>…same shape as <manufacturer>…</eu-responsible-person>
        <model/>
        <safety-notices>
          <notice locale="…"/>
        </safety-notices>
        <safety-documents>
          <document type="…" locale="…"><url/></document>
        </safety-documents>
        <certifications>
          <certification><code/> <notified-body/></certification>
        </certifications>
      </gpsr>
    </product>
  </products>
</sylius-import>
```

---

## Root element `<sylius-import>`

| Attribute | Required | Description | Example |
|---|---|---|---|
| `version` | yes | Schema version | `2.0` |
| `default-locale` | yes | Primary content language | `en_US` |
| `channel` | no | Sylius channel code | `default` |

```xml
<sylius-import version="2.0" default-locale="en_US" channel="default">
```

---

## `<product>`

| Attribute | Required | Description |
|---|---|---|
| `enabled` | no | Whether the product is active, default `true` |

| Child element | Required | Description |
|---|---|---|
| `<code>` | * | Our internal product code |
| `<external-code>` | * | Your internal product code |
| `<manufacturer>` | no | Who **physically manufactured** the product (e.g. `Foxconn Technology Group`). For GPSR purposes the authoritative source is `<gpsr><manufacturer>` (see below) |
| `<brand>` | no | Marketing **brand** under which the product is sold (e.g. `Apple`, `Nike`). Often equals the manufacturer, but not always — OEM, private labels, licensed brands |
| `<gpsr>` | no | GPSR compliance block (EU 2023/988) — see [GPSR compliance](#gpsr-compliance-eu-2023988) |

*At least one of `code` / `external-code` must be present.*

> **`<manufacturer>` vs `<brand>`:** use both when they differ. If your
> supplier only knows one of them, fill only that one — the importer
> treats `<brand>` as the display brand and falls back to `<manufacturer>`
> when no brand is given.

```xml
<!-- External supplier — your code only; brand differs from manufacturer -->
<product enabled="true">
    <external-code>BB-987654</external-code>
    <manufacturer>Foxconn Technology Group</manufacturer>
    <brand>Apple</brand>
    ...
</product>

<!-- Sylius to Sylius — our internal code -->
<product enabled="true">
    <code>IPHONE-15-PRO</code>
    <manufacturer>Foxconn Technology Group</manufacturer>
    <brand>Apple</brand>
    ...
</product>
```

---

## `<translation>` (product)

| Attribute | Description |
|---|---|
| `locale` | Language; falls back to `default-locale` if omitted |

| Child element | Required | Description |
|---|---|---|
| `<name>` | yes | Product name |
| `<slug>` | no | URL slug; generated from name by the importer if omitted |
| `<short-description>` | no | Short description (plain text) |
| `<description>` | no | Long description (HTML allowed; wrap in CDATA) |
| `<meta-title>` | no | SEO title; falls back to name if omitted |
| `<meta-description>` | no | SEO meta description |

**Minimal example:**
```xml
<translations>
    <translation>
        <name>Apple iPhone 15 Pro</name>
    </translation>
</translations>
```

**Full example:**
```xml
<translations>
    <translation locale="en_US">
        <name>Apple iPhone 15 Pro</name>
        <slug>apple-iphone-15-pro</slug>
        <short-description>The most powerful iPhone ever.</short-description>
        <description><![CDATA[<p>iPhone 15 Pro with A17 Pro chip.</p>]]></description>
        <meta-title>Apple iPhone 15 Pro | Buy online</meta-title>
        <meta-description>Buy Apple iPhone 15 Pro at the best price.</meta-description>
    </translation>
    <translation locale="de_DE">
        <name>Apple iPhone 15 Pro</name>
    </translation>
</translations>
```

> **Note on HTML in `<description>`:** wrap the HTML in `<![CDATA[ ... ]]>`
> so you do not have to escape `<`, `>` or `&`. If you prefer, you can also
> escape them manually (`&lt;p&gt;...&lt;/p&gt;`) — both forms are valid.

---

## `<taxons>` (categories)

| Attribute (on `<taxons>`) | Description |
|---|---|
| `main` | Code of the main taxon; first taxon is used if omitted |

| Child element (of `<taxon>`) | Description |
|---|---|
| `<code>` | Our internal taxon code |
| `<external-code>` | Your internal taxon code |
| `<name>` | Human-readable taxon name from your system |

```xml
<!-- External supplier — human-readable names -->
<taxons>
    <taxon>
        <external-code>CAT-SMART</external-code>
        <name>Smartphones</name>
    </taxon>
    <taxon>
        <external-code>CAT-APPLE</external-code>
        <name>Apple</name>
    </taxon>
</taxons>

<!-- Sylius to Sylius — our internal codes -->
<taxons main="electronics-phones">
    <taxon><code>electronics-phones</code></taxon>
    <taxon><code>electronics</code></taxon>
</taxons>
```

---

## `<attributes>`

| Child element (of `<attribute>`) | Description |
|---|---|
| `<code>` | Our internal attribute code |
| `<name>` | Human-readable attribute name from your system |
| `<external-code>` | Your internal attribute code |
| `<value>` | Human-readable attribute value |
| `<value-code>` | Value code |
| `<external-value-code>` | Your internal value code |

```xml
<!-- External supplier -->
<attributes>
    <attribute>
        <name>Brand</name>
        <external-code>ATTR-BRD</external-code>
        <value>Apple</value>
        <external-value-code>BRD-001</external-value-code>
    </attribute>
    <attribute>
        <name>Screen size</name>
        <value>6.1"</value>
    </attribute>
</attributes>

<!-- Sylius to Sylius -->
<attributes>
    <attribute>
        <code>brand</code>
        <value-code>apple</value-code>
    </attribute>
    <attribute>
        <code>screen_size</code>
        <value>6.1</value>
    </attribute>
</attributes>
```

---

## `<images>`

| Attribute (on `<image>`) | Description |
|---|---|
| `type` | `main` / `additional` / `thumbnail`, default `additional` |

| Child element (of `<image>`) | Required | Description |
|---|---|---|
| `<url>` | * | Absolute image URL |
| `<path>` | * | Relative path on disk (Sylius export) |

*At least one of `url` / `path` must be present.*

```xml
<images>
    <image type="main">
        <url>https://cdn.supplier.eu/product/main.jpg?v=2&amp;size=800</url>
    </image>
    <image type="additional">
        <url>https://cdn.supplier.eu/product/side.jpg</url>
    </image>
</images>
```

---

## `<variant>`

| Attribute | Description |
|---|---|
| `enabled` | Whether the variant is active, default `true` |
| `condition` | Physical condition: `new` / `used` / `refurbished`, default `new` |

| Child element | Required | Description |
|---|---|---|
| `<code>` | * | Our internal variant code (EAN, SKU...) |
| `<external-code>` | * | Your internal variant code |
| `<ean>` | no | EAN-13 barcode (e.g. `5901234123457`); omit if not available |

*At least one of `code` / `external-code` must be present.*

### `<translation>` (variant)

| Attribute | Description |
|---|---|
| `locale` | Language; falls back to `default-locale` if omitted |

| Child element | Required | Description |
|---|---|---|
| `<name>` | yes | Variant name |
| `<slug>` | no | URL slug; generated by the importer if omitted |

### `<options>`

| Attribute (on `<option>`) | Description |
|---|---|
| `locale` | Language of `<name>`/`<value>` if different from `default-locale` |

| Child element (of `<option>`) | Description |
|---|---|
| `<code>` | Our internal option code (e.g. `color`) |
| `<name>` | Human-readable option name (e.g. `Color`) |
| `<external-code>` | Your internal option code |
| `<value>` | Human-readable option value (e.g. `Red`) |
| `<value-code>` | Option value code |
| `<external-value-code>` | Your internal option value code |

```xml
<!-- External supplier -->
<options>
    <option>
        <name>Color</name>
        <external-code>OPT-COL</external-code>
        <value>Black</value>
        <external-value-code>COL-BLK</external-value-code>
    </option>
    <option>
        <name>Storage</name>
        <external-code>OPT-MEM</external-code>
        <value>128 GB</value>
        <external-value-code>MEM-128</external-value-code>
    </option>
</options>

<!-- Sylius to Sylius -->
<options>
    <option>
        <code>color</code>
        <value-code>color_black</value-code>
    </option>
    <option>
        <code>storage</code>
        <value-code>storage_128</value-code>
    </option>
</options>
```

### `<price>`

All price attributes are typed (currency pattern / integer / decimal) so
they stay as attributes — there is no escaping concern.

| Attribute | Required | Description |
|---|---|---|
| `currency` | yes | ISO 4217 currency code (`EUR`, `CZK`, `USD`...) |
| `amount` | * | **Net** price (without VAT), in the **smallest currency unit** (cents) |
| `vat-amount` | * | **Gross** price (with VAT), in the **smallest currency unit** (cents) |
| `vat` | ** | VAT rate in percent (e.g. `20`, `21`, `10`, `5.5`) — no `%` sign |

*\* At least one of `amount` / `vat-amount` must be present.*
*\*\* `vat` is **required** whenever `vat-amount` is supplied, so the importer can derive the net amount.*

> **Important:** `amount` and `vat-amount` are always integers in cents.
> Example: `119900` = 1,199.00 EUR — `143880` = 1,438.80 EUR

**When to use which:**

- Supplier is a **VAT payer** and reports net prices → use `amount` (optionally add `vat` to carry the rate)
- Supplier (or external feed) reports **gross prices only** → use `vat-amount` + `vat`
- Both are known → supply all three; the importer reconciles them against the `vat` rate

```xml
<!-- Net price only (supplier quotes without VAT) -->
<price currency="EUR" amount="119900" />

<!-- Gross price only (typical external supplier feed) -->
<price currency="EUR" vat-amount="143880" vat="20" />

<!-- Net + VAT rate (Sylius-to-Sylius; carries the rate for re-use) -->
<price currency="EUR" amount="119900" vat="20" />

<!-- Both net and gross — reconciled against vat -->
<price currency="EUR" amount="119900" vat-amount="143880" vat="20" />
```

### `<stock>`

```xml
<stock on-hand="50" />
```

### `<dimensions>`

Fixed units: `weight` in **kg**, all other dimensions in **mm**.

```xml
<dimensions weight="0.187" width="71.5" height="146.6" depth="8.25" />
```

---

## GPSR compliance (EU 2023/988)

The EU **General Product Safety Regulation** (GPSR, Regulation (EU) 2023/988)
has been in force since **13 December 2024**. Article 19 requires online
marketplaces to display, for every product offered to EU consumers, the
manufacturer's identity and contact data, an EU responsible person when
the manufacturer is outside the EU, and safety warnings in the consumer's
language.

The optional `<gpsr>` block carries this data. It sits at the end of
`<product>`, after `<variants>`. The block as a whole is optional — but
**if it is present**, it must at minimum carry `<manufacturer>` with the
required identification fields.

```xml
<product>
    ...
    <variants>...</variants>

    <gpsr>
        <manufacturer>
            <name>Apple Inc.</name>
            <trademark>Apple</trademark>
            <street>One Apple Park Way</street>
            <city>Cupertino</city>
            <postal-code>95014</postal-code>
            <country>US</country>
            <email>productsafety@apple.com</email>
            <phone>+1-408-996-1010</phone>
        </manufacturer>
        <eu-responsible-person>
            <name>Apple Distribution International Ltd.</name>
            <street>Hollyhill Industrial Estate, Hollyhill</street>
            <city>Cork</city>
            <postal-code>T23 YK84</postal-code>
            <country>IE</country>
            <email>eu-productsafety@apple.com</email>
        </eu-responsible-person>
        <model>A3102</model>
        <safety-notices>
            <notice locale="en_US"><![CDATA[Charge only with original adapter.]]></notice>
            <notice locale="de_DE"><![CDATA[Nur mit originalem Netzteil laden.]]></notice>
        </safety-notices>
        <safety-documents>
            <document type="user-manual" locale="en_US">
                <url>https://manuals.apple.com/iphone-15-pro/en_US/manual.pdf</url>
            </document>
            <document type="declaration-of-conformity">
                <url>https://www.apple.com/compliance/iphone-15-pro/doc.pdf</url>
            </document>
        </safety-documents>
        <certifications>
            <certification><code>CE</code></certification>
            <certification><code>RoHS</code></certification>
        </certifications>
    </gpsr>
</product>
```

### `<gpsr>` child elements

| Child element | Required | Description |
|---|---|---|
| `<manufacturer>` | **yes (when `<gpsr>` is present)** | Structured manufacturer identity (Art. 9(5), 19(4)(a)) |
| `<eu-responsible-person>` | \* | EU responsible person (Art. 16) — required when the manufacturer is established outside the EU |
| `<model>` | no | Product type / model identifier, e.g. `A3102` (Art. 19(4)(c)) |
| `<safety-notices>` | no | Short inline warnings translated per locale |
| `<safety-documents>` | no | Links to external safety documents (PDF, web page) |
| `<certifications>` | no | Compliance marks (`CE`, `RoHS`, `FCC`, `REACH`, `UKCA`, …) |

*\* The "manufacturer outside EU → EU responsible person" rule cannot be
expressed in XSD 1.0 and is enforced by the importer — same pattern as
the "at least one of `code` / `external-code`" rule.*

### `<manufacturer>` / `<eu-responsible-person>`

Both elements share the same shape (`GpsrPartyType` in the XSD). All
string content lives in child elements so CDATA is available for names
with apostrophes, ampersands or non-ASCII characters.

| Child element | Required | Description |
|---|---|---|
| `<name>` | yes | Legal name of the entity (Art. 9(5)) |
| `<trademark>` | no | Registered trade name or registered trademark, if any |
| `<street>` | yes | Street address |
| `<city>` | yes | City |
| `<postal-code>` | yes | Postal code |
| `<country>` | yes | ISO 3166-1 alpha-2 country code (`SK`, `DE`, `US`, `CN`, …) |
| `<email>` | yes | Electronic address (Art. 9(5)) |
| `<phone>` | no | Phone number — **not required** by GPSR but useful where available |

> **Why is `<phone>` optional?** GPSR Art. 9(5) requires a **postal
> address** and an **electronic address**. "Electronic address" is
> satisfied by email alone; a phone number is nice-to-have but not
> compulsory.

### `<safety-notices>`

Short warning texts shown inline on the product page. Each `<notice>`
is optionally tagged with a `locale` attribute — the importer falls
back to `default-locale` from the root element when omitted.

```xml
<safety-notices>
    <notice locale="en_US"><![CDATA[Keep out of reach of children.]]></notice>
    <notice locale="de_DE"><![CDATA[Außerhalb der Reichweite von Kindern aufbewahren.]]></notice>
</safety-notices>
```

### `<safety-documents>`

References to external safety PDFs or web pages (user manuals,
declaration of conformity, safety data sheets, recall notices…).

| Attribute (on `<document>`) | Required | Description |
|---|---|---|
| `type` | yes | Document kind (enum, see below) |
| `locale` | no | Language of the document; omit for universal documents |

| Child element (of `<document>`) | Required | Description |
|---|---|---|
| `<url>` | yes | Absolute URL to the document |

**Allowed values of `type`:**

| `type` | Meaning |
|---|---|
| `user-manual` | Usage / operating instructions |
| `declaration-of-conformity` | EU Declaration of Conformity (DoC) |
| `safety-data-sheet` | Safety / material safety data sheet (SDS / MSDS) |
| `safety-instructions` | Separate safety insert or quick-start safety card |
| `test-report` | Lab or compliance test report |
| `recall-notice` | Recall or corrective-action notice |
| `other` | Anything else |

```xml
<safety-documents>
    <document type="user-manual" locale="en_US">
        <url>https://docs.example.com/product-123/manual-en.pdf</url>
    </document>
    <document type="declaration-of-conformity">
        <url>https://docs.example.com/product-123/doc.pdf</url>
    </document>
</safety-documents>
```

### `<certifications>`

Free-form compliance marks. `<code>` is mandatory; `<notified-body>` is
optional and carries the notified body number when applicable (e.g. `0086`
alongside a `CE` mark).

```xml
<certifications>
    <certification>
        <code>CE</code>
        <notified-body>0086</notified-body>
    </certification>
    <certification>
        <code>RoHS</code>
    </certification>
</certifications>
```

---

## Multi-file imports (manifest)

When your export contains more than ~5,000 products, split it into multiple `sylius-import` files and include a manifest. The importer processes each file in the order listed.

**Manifest file** (`sylius-import-manifest.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sylius-import-manifest version="2.0"
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xsi:noNamespaceSchemaLocation="https://elcuro.github.io/sylius-import-schema/sylius-import-2.0.xsd">
    <files>
        <file>products-001.xml</file>
        <file>products-002.xml</file>
        <file>https://cdn.example.com/exports/2026-04/products-003.xml</file>
    </files>
</sylius-import-manifest>
```

Each `<file>` element contains either a **relative path** (resolved against the manifest's own location) or an **absolute `http(s)` URL** that the importer fetches directly. Both forms can be mixed within a single manifest — useful when part of the export is bundled next to the manifest and the rest is served from a CDN.

**Recommended directory layout:**

```
export/
├── sylius-import-manifest.xml
├── products-001.xml
├── products-002.xml
└── products-003.xml
```

**Recommended size:** max 5,000 products per file.

Each file may repeat `<taxons>` and `<attributes>` — the importer performs upserts so duplicates are not a problem.

---

## Public test fixtures

Generated fixtures are hosted on GitHub Pages so you can download them directly
(e.g. for load-testing the importer or pointing a supplier at a realistic example):

| File | Products | URL |
|---|---:|---|
| `tests/test-3.xml` | 3 | https://elcuro.github.io/sylius-import-schema/tests/test-3.xml |
| `tests/test-50.xml` | 50 | https://elcuro.github.io/sylius-import-schema/tests/test-50.xml |
| `tests/test-100.xml` | 100 | https://elcuro.github.io/sylius-import-schema/tests/test-100.xml |
| `tests/test-500.xml` | 500 | https://elcuro.github.io/sylius-import-schema/tests/test-500.xml |
| `tests/test-500-part-a.xml` | 250 | https://elcuro.github.io/sylius-import-schema/tests/test-500-part-a.xml |
| `tests/test-500-part-b.xml` | 250 | https://elcuro.github.io/sylius-import-schema/tests/test-500-part-b.xml |
| `tests/test-500-manifest.xml` | manifest (part-a + part-b) | https://elcuro.github.io/sylius-import-schema/tests/test-500-manifest.xml |

All fixtures are generated by `generate_test_xml.py` and validated against
`sylius-import-2.0.xsd` before every release. Image URLs use
[dummyimage.com](https://dummyimage.com/) placeholders so they actually resolve.

```bash
# Download and validate the smallest fixture
curl -sO https://elcuro.github.io/sylius-import-schema/tests/test-3.xml
xmllint --schema sylius-import-2.0.xsd test-3.xml --noout
```

---

## Common errors

### Error: `Schemas validity error: ... is not a valid value`

Check the `locale` format — it must follow the pattern `xx_XX` (e.g. `en_US`, not `en-US` or `en`).

### Error: `amount` contains a decimal point

```xml
<!-- wrong -->
<price currency="EUR" amount="1199.00" />

<!-- correct — use cents -->
<price currency="EUR" amount="119900" />
```

### Error: `<name>` is missing on `<translation>`

`<name>` is the only required child element on `<translation>`.

### Error: unescaped `&` in text content

Use CDATA or escape ampersands as `&amp;`:

```xml
<!-- wrong -->
<name>Ben & Jerry's</name>

<!-- correct — via CDATA -->
<name><![CDATA[Ben & Jerry's]]></name>

<!-- or via entity -->
<name>Ben &amp; Jerry's</name>
```

---

## Contact

For questions about the schema or the import process, contact us at:
**import@your-company.com**
