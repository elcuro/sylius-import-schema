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
      <translations>
        <translation />
      </translations>
      <taxons>
        <taxon />
      </taxons>
      <attributes>
        <attribute />
      </attributes>
      <images>
        <image />
      </images>
      <variants>
        <variant>
          <translation />
          <options>
            <option />
          </options>
          <price />
          <stock />
          <dimensions />
        </variant>
      </variants>
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
| `code` | * | Our internal product code |
| `external-code` | * | Your internal product code |
| `enabled` | no | Whether the product is active, default `true` |
| `manufacturer` | no | Manufacturer name (e.g. `Apple`, `Samsung`) |

*At least one of `code` / `external-code` must be present.*

```xml
<!-- External supplier — your code only -->
<product external-code="BB-987654">

<!-- Sylius to Sylius — our internal code -->
<product code="IPHONE-15-PRO">

<!-- Both — our code and your code -->
<product code="IPHONE-15-PRO" external-code="BB-987654">
```

---

## `<translation>` (product)

| Attribute | Required | Description |
|---|---|---|
| `name` | yes | Product name |
| `locale` | no | Language; falls back to `default-locale` if omitted |
| `slug` | no | URL slug; generated from name by the importer if omitted |
| `short-description` | no | Short description (plain text) |
| `description` | no | Long description (HTML, must be escaped) |
| `meta-title` | no | SEO title; falls back to name if omitted |
| `meta-description` | no | SEO meta description |

**Minimal example:**
```xml
<translations>
    <translation name="Apple iPhone 15 Pro" />
</translations>
```

**Full example:**
```xml
<translations>
    <translation locale="en_US"
                 name="Apple iPhone 15 Pro"
                 slug="apple-iphone-15-pro"
                 short-description="The most powerful iPhone ever."
                 description="&lt;p&gt;iPhone 15 Pro with A17 Pro chip.&lt;/p&gt;"
                 meta-title="Apple iPhone 15 Pro | Buy online"
                 meta-description="Buy Apple iPhone 15 Pro at the best price." />
    <translation locale="de_DE"
                 name="Apple iPhone 15 Pro" />
</translations>
```

> **Note on HTML in description:** The characters `<` and `>` must be escaped as `&lt;` and `&gt;`.
> Example: `&lt;p&gt;Product description.&lt;/p&gt;`

---

## `<taxons>` (categories)

| Attribute | Where | Description |
|---|---|---|
| `main` | on `<taxons>` | Code of the main taxon; first taxon is used if omitted |
| `code` | on `<taxon>` | Our internal taxon code |
| `name` | on `<taxon>` | Human-readable taxon name from your system |
| `external-code` | on `<taxon>` | Your internal taxon code |

```xml
<!-- External supplier — human-readable names -->
<taxons>
    <taxon name="Smartphones"   external-code="CAT-SMART" />
    <taxon name="Apple"         external-code="CAT-APPLE" />
</taxons>

<!-- Sylius to Sylius — our internal codes -->
<taxons main="electronics-phones">
    <taxon code="electronics-phones" />
    <taxon code="electronics" />
</taxons>
```

---

## `<attributes>`

| Attribute | Description |
|---|---|
| `code` | Our internal attribute code |
| `name` | Human-readable attribute name from your system |
| `external-code` | Your internal attribute code |
| `value` | Human-readable attribute value |
| `value-code` | Value code |
| `external-value-code` | Your internal value code |

```xml
<!-- External supplier -->
<attributes>
    <attribute name="Brand"  external-code="ATTR-BRD"
               value="Apple" external-value-code="BRD-001" />
    <attribute name="Screen size" value="6.1" />
</attributes>

<!-- Sylius to Sylius -->
<attributes>
    <attribute code="brand"       value-code="apple" />
    <attribute code="screen_size" value="6.1" />
</attributes>
```

---

## `<images>`

| Attribute | Required | Description |
|---|---|---|
| `url` | * | Absolute image URL |
| `path` | * | Relative path on disk (Sylius export) |
| `type` | no | `main` / `additional` / `thumbnail`, default `additional` |

*At least one of `url` / `path` must be present.*

```xml
<images>
    <image url="https://cdn.supplier.eu/product/main.jpg" type="main" />
    <image url="https://cdn.supplier.eu/product/side.jpg" type="additional" />
</images>
```

---

## `<variant>`

| Attribute | Required | Description |
|---|---|---|
| `code` | * | Our internal variant code (EAN, SKU...) |
| `external-code` | * | Your internal variant code |
| `enabled` | no | Whether the variant is active, default `true` |

*At least one of `code` / `external-code` must be present.*

### `<translation>` (variant)

| Attribute | Required | Description |
|---|---|---|
| `name` | yes | Variant name |
| `locale` | no | Language; falls back to `default-locale` if omitted |
| `slug` | no | URL slug; generated by the importer if omitted |

### `<options>`

| Attribute | Description |
|---|---|
| `code` | Our internal option code (e.g. `color`) |
| `name` | Human-readable option name (e.g. `Color`) |
| `external-code` | Your internal option code |
| `value` | Human-readable option value (e.g. `Red`) |
| `value-code` | Option value code |
| `external-value-code` | Your internal option value code |
| `locale` | Language of `name`/`value` if different from `default-locale` |

```xml
<!-- External supplier -->
<options>
    <option name="Color"    external-code="OPT-COL"
            value="Black"   external-value-code="COL-BLK" />
    <option name="Storage"  external-code="OPT-MEM"
            value="128 GB"  external-value-code="MEM-128" />
</options>

<!-- Sylius to Sylius -->
<options>
    <option code="color"   value-code="color_black" />
    <option code="storage" value-code="storage_128" />
</options>
```

### `<price>`

| Attribute | Required | Description |
|---|---|---|
| `currency` | yes | ISO 4217 currency code (`EUR`, `CZK`, `USD`...) |
| `amount` | yes | Price in the **smallest currency unit** (cents) |

> **Important:** `amount` is always an integer in cents.
> Example: `119900` = 1,199.00 EUR

```xml
<price currency="EUR" amount="119900" />
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

## Multi-file imports (manifest)

When your export contains more than ~5,000 products, split it into multiple `sylius-import` files and include a manifest. The importer processes each file in the order listed.

**Manifest file** (`sylius-import-manifest.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sylius-import-manifest version="2.0"
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xsi:noNamespaceSchemaLocation="https://elcuro.github.io/sylius-import-schema/sylius-import-2.0.xsd">
    <files>
        <file path="products-001.xml" />
        <file path="products-002.xml" />
        <file path="products-003.xml" />
    </files>

</sylius-import-manifest>
```

Each file in `<files>` is a standard `sylius-import` document. Paths are relative to the manifest file.

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

### Error: HTML in `description` is not escaped

```xml
<!-- wrong -->
<translation description="<p>Product description.</p>" />

<!-- correct -->
<translation description="&lt;p&gt;Product description.&lt;/p&gt;" />
```

### Error: `name` is missing on `<translation>`

`name` is the only required attribute on `<translation>`.

---

## Contact

For questions about the schema or the import process, contact us at:
**import@your-company.com**
