#!/usr/bin/env python3
"""
Generate test sylius-import XML files with realistic product data.
Produces: test-3.xml, test-50.xml, test-100.xml, test-500.xml

All string content is emitted as child elements (matching the v2.0
design rule — attributes reserved for typed values only).
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import random
import os

random.seed(42)

# ── Data pools ────────────────────────────────────────────────────────────────

CATEGORIES = [
    ("electronics",          None,              "Electronics"),
    ("electronics-phones",   "electronics",     "Phones"),
    ("electronics-laptops",  "electronics",     "Laptops"),
    ("electronics-audio",    "electronics",     "Audio"),
    ("electronics-cameras",  "electronics",     "Cameras"),
    ("clothing",             None,              "Clothing"),
    ("clothing-mens",        "clothing",        "Men's Clothing"),
    ("clothing-womens",      "clothing",        "Women's Clothing"),
    ("clothing-kids",        "clothing",        "Kids' Clothing"),
    ("sports",               None,              "Sports & Outdoors"),
    ("sports-fitness",       "sports",          "Fitness"),
    ("sports-cycling",       "sports",          "Cycling"),
    ("home-garden",          None,              "Home & Garden"),
    ("home-kitchen",         "home-garden",     "Kitchen"),
    ("home-furniture",       "home-garden",     "Furniture"),
    ("toys",                 None,              "Toys & Games"),
    ("books",                None,              "Books"),
    ("beauty",               None,              "Beauty & Health"),
]

ATTRIBUTE_SETS = {
    "electronics": [
        ("brand",       "Brand",        ["Samsung", "Apple", "Sony", "LG", "Philips", "Bosch"]),
        ("color",       "Color",        ["Black", "White", "Silver", "Gold", "Space Gray"]),
        ("warranty",    "Warranty",     ["12 months", "24 months", "36 months"]),
        ("country",     "Country of origin", ["South Korea", "USA", "Japan", "China"]),
    ],
    "clothing": [
        ("brand",       "Brand",        ["Nike", "Adidas", "Zara", "H&M", "Levi's", "Puma"]),
        ("material",    "Material",     ["Cotton", "Polyester", "Wool", "Linen", "Silk"]),
        ("color",       "Color",        ["Black", "White", "Navy", "Red", "Green", "Grey"]),
        ("fit",         "Fit",          ["Regular", "Slim", "Relaxed", "Oversized"]),
    ],
    "sports": [
        ("brand",       "Brand",        ["Nike", "Adidas", "Under Armour", "Puma", "Reebok"]),
        ("color",       "Color",        ["Black", "White", "Blue", "Red", "Yellow"]),
        ("material",    "Material",     ["Mesh", "Neoprene", "Carbon fiber", "Aluminium"]),
    ],
    "home-garden": [
        ("brand",       "Brand",        ["IKEA", "Bosch", "Philips", "Dyson", "Electrolux"]),
        ("color",       "Color",        ["White", "Black", "Beige", "Grey", "Natural wood"]),
        ("material",    "Material",     ["Plastic", "Metal", "Wood", "Glass", "Ceramic"]),
    ],
    "default": [
        ("brand",       "Brand",        ["Generic", "Premium", "Basic", "Pro", "Elite"]),
        ("color",       "Color",        ["Black", "White", "Blue", "Red"]),
    ],
}

OPTION_SETS = {
    "clothing": [
        ("size",  "Size",  ["XS", "S", "M", "L", "XL", "XXL"]),
        ("color", "Color", ["Black", "White", "Navy", "Red", "Green", "Grey", "Blue"]),
    ],
    "electronics-phones": [
        ("storage", "Storage", ["64 GB", "128 GB", "256 GB", "512 GB"]),
        ("color",   "Color",   ["Black", "White", "Blue", "Gold", "Silver"]),
    ],
    "electronics-laptops": [
        ("storage", "Storage", ["256 GB SSD", "512 GB SSD", "1 TB SSD"]),
        ("ram",     "RAM",     ["8 GB", "16 GB", "32 GB"]),
    ],
    "electronics-audio": [
        ("color",      "Color",      ["Black", "White", "Silver"]),
        ("connection", "Connection", ["Wired", "Wireless", "Bluetooth 5.0"]),
    ],
    "sports-fitness": [
        ("size",   "Size",   ["XS", "S", "M", "L", "XL"]),
        ("color",  "Color",  ["Black", "White", "Blue", "Red"]),
    ],
    "default": [
        ("color", "Color", ["Black", "White", "Blue"]),
        ("size",  "Size",  ["S", "M", "L"]),
    ],
}

PRODUCT_TEMPLATES = [
    # (name_template, category, subcategory, price_range, weight_range, manufacturer)
    ("Samsung Galaxy S{n} Ultra",      "electronics",  "electronics-phones",   (79900, 129900), (0.228, 0.250), "Samsung"),
    ("Apple iPhone {n} Pro",           "electronics",  "electronics-phones",   (99900, 149900), (0.187, 0.221), "Apple"),
    ("Sony WH-{n}000XM5 Headphones",   "electronics",  "electronics-audio",    (24900,  39900), (0.250, 0.300), "Sony"),
    ("LG OLED{n}C Laptop",             "electronics",  "electronics-laptops",  (89900, 179900), (1.200, 2.100), "LG"),
    ("Nike Air Max {n}",               "clothing",     "clothing-mens",        ( 8990,  14990), (0.300, 0.450), "Nike"),
    ("Adidas Ultraboost {n}",          "clothing",     "clothing-mens",        ( 9990,  16990), (0.310, 0.460), "Adidas"),
    ("Zara Slim Fit Shirt #{n}",       "clothing",     "clothing-mens",        ( 2990,   4990), (0.200, 0.300), "Zara"),
    ("H&M Women's Dress #{n}",         "clothing",     "clothing-womens",      ( 1990,   3990), (0.250, 0.350), "H&M"),
    ("Specialized Bike Part #{n}",     "sports",       "sports-cycling",       ( 4990,  29900), (0.500, 2.000), "Specialized"),
    ("Under Armour Training Set #{n}", "sports",       "sports-fitness",       ( 3990,   8990), (0.400, 0.600), "Under Armour"),
    ("IKEA KALLAX Shelf #{n}",         "home-garden",  "home-furniture",       ( 4990,  12990), (15.00, 30.00), "IKEA"),
    ("Philips Airfryer #{n}",          "home-garden",  "home-kitchen",         ( 7990,  14990), (2.500, 4.000), "Philips"),
    ("Bosch Hand Blender #{n}",        "home-garden",  "home-kitchen",         ( 2990,   6990), (0.800, 1.200), "Bosch"),
    ("Dyson V{n} Vacuum",              "home-garden",  "home-garden",          (29900,  59900), (2.600, 3.100), "Dyson"),
    ("Canon EOS R{n}",                 "electronics",  "electronics-cameras",  (89900, 199900), (0.650, 0.900), "Canon"),
]

DE_PREFIXES  = ["Super", "Premium", "Ultra", "Pro", "Elite", "Advanced", "Smart", "Eco"]
FR_SUFFIXES  = ["Edition", "Collection", "Série", "Modèle", "Version"]

# ── GPSR (EU 2023/988) data pools ────────────────────────────────────────────
#
# Per-brand manufacturer party. Country determines whether an EU responsible
# person (Art. 16) is required. Addresses are illustrative — they roughly
# reflect the real HQ but should not be treated as compliance data.
MANUFACTURER_GPSR = {
    "Samsung": {
        "name": "Samsung Electronics Co., Ltd.",
        "trademark": "Samsung",
        "street": "129 Samsung-ro, Yeongtong-gu", "city": "Suwon",
        "postal-code": "16677", "country": "KR",
        "email": "productsafety@samsung.com", "phone": "+82-31-200-1114",
    },
    "Apple": {
        "name": "Apple Inc.", "trademark": "Apple",
        "street": "One Apple Park Way", "city": "Cupertino",
        "postal-code": "95014", "country": "US",
        "email": "productsafety@apple.com", "phone": "+1-408-996-1010",
    },
    "Sony": {
        "name": "Sony Group Corporation", "trademark": "Sony",
        "street": "1-7-1 Konan, Minato-ku", "city": "Tokyo",
        "postal-code": "108-0075", "country": "JP",
        "email": "productsafety@sony.com",
    },
    "LG": {
        "name": "LG Electronics Inc.", "trademark": "LG",
        "street": "128 Yeoui-daero, Yeongdeungpo-gu", "city": "Seoul",
        "postal-code": "07336", "country": "KR",
        "email": "productsafety@lge.com",
    },
    "Philips": {
        "name": "Koninklijke Philips N.V.", "trademark": "Philips",
        "street": "Amstelplein 2", "city": "Amsterdam",
        "postal-code": "1096 BC", "country": "NL",
        "email": "productsafety@philips.com",
    },
    "Bosch": {
        "name": "Robert Bosch GmbH", "trademark": "Bosch",
        "street": "Robert-Bosch-Platz 1", "city": "Gerlingen",
        "postal-code": "70839", "country": "DE",
        "email": "productsafety@bosch.com",
    },
    "Nike": {
        "name": "Nike, Inc.", "trademark": "Nike",
        "street": "One Bowerman Drive", "city": "Beaverton",
        "postal-code": "97005", "country": "US",
        "email": "productsafety@nike.com",
    },
    "Adidas": {
        "name": "adidas AG", "trademark": "adidas",
        "street": "Adi-Dassler-Straße 1", "city": "Herzogenaurach",
        "postal-code": "91074", "country": "DE",
        "email": "productsafety@adidas.com",
    },
    "Zara": {
        "name": "Industria de Diseño Textil, S.A.", "trademark": "ZARA",
        "street": "Avenida de la Diputación s/n", "city": "Arteixo",
        "postal-code": "15142", "country": "ES",
        "email": "productsafety@inditex.com",
    },
    "H&M": {
        "name": "H & M Hennes & Mauritz AB", "trademark": "H&M",
        "street": "Mäster Samuelsgatan 46A", "city": "Stockholm",
        "postal-code": "106 38", "country": "SE",
        "email": "productsafety@hm.com",
    },
    "Puma": {
        "name": "PUMA SE", "trademark": "PUMA",
        "street": "Puma Way 1", "city": "Herzogenaurach",
        "postal-code": "91074", "country": "DE",
        "email": "productsafety@puma.com",
    },
    "Under Armour": {
        "name": "Under Armour, Inc.", "trademark": "Under Armour",
        "street": "1020 Hull Street", "city": "Baltimore",
        "postal-code": "21230", "country": "US",
        "email": "productsafety@underarmour.com",
    },
    "Reebok": {
        "name": "Reebok International Ltd.", "trademark": "Reebok",
        "street": "25 Drydock Avenue", "city": "Boston",
        "postal-code": "02210", "country": "US",
        "email": "productsafety@reebok.com",
    },
    "Specialized": {
        "name": "Specialized Bicycle Components, Inc.", "trademark": "Specialized",
        "street": "15130 Concord Circle", "city": "Morgan Hill",
        "postal-code": "95037", "country": "US",
        "email": "productsafety@specialized.com",
    },
    "IKEA": {
        "name": "IKEA of Sweden AB", "trademark": "IKEA",
        "street": "Tulpanvägen 8", "city": "Älmhult",
        "postal-code": "343 36", "country": "SE",
        "email": "productsafety@ikea.com",
    },
    "Dyson": {
        "name": "Dyson Technology Ltd.", "trademark": "Dyson",
        "street": "Tetbury Hill", "city": "Malmesbury",
        "postal-code": "SN16 0RP", "country": "GB",
        "email": "productsafety@dyson.com",
    },
    "Electrolux": {
        "name": "Electrolux AB", "trademark": "Electrolux",
        "street": "S:t Göransgatan 143", "city": "Stockholm",
        "postal-code": "105 45", "country": "SE",
        "email": "productsafety@electrolux.com",
    },
    "Canon": {
        "name": "Canon Inc.", "trademark": "Canon",
        "street": "30-2 Shimomaruko 3-chome, Ohta-ku", "city": "Tokyo",
        "postal-code": "146-8501", "country": "JP",
        "email": "productsafety@canon.com",
    },
    # Fashion / generic brands without a dedicated entry fall back to this one.
    "Levi's": {
        "name": "Levi Strauss & Co.", "trademark": "Levi's",
        "street": "1155 Battery Street", "city": "San Francisco",
        "postal-code": "94111", "country": "US",
        "email": "productsafety@levi.com",
    },
}

# EU member countries — used to decide whether eu-responsible-person applies.
EU_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE",
}

# Generic EU responsible person used for non-EU manufacturers.
DEFAULT_EU_REP = {
    "name": "Example EU Compliance B.V.",
    "street": "Rokin 25", "city": "Amsterdam",
    "postal-code": "1012 KK", "country": "NL",
    "email": "gpsr@example-eu-compliance.example",
    "phone": "+31-20-555-0123",
}

SAFETY_NOTICE_POOL = {
    "en_US": [
        "Keep out of reach of children. Not suitable for children under 36 months.",
        "Do not immerse in water. Clean with a dry cloth only.",
        "Charge only with the supplied adapter. Do not use damaged cables.",
        "Use only as intended. Read the user manual before first use.",
    ],
    "de_DE": [
        "Außerhalb der Reichweite von Kindern aufbewahren. Nicht für Kinder unter 36 Monaten.",
        "Nicht in Wasser tauchen. Nur mit trockenem Tuch reinigen.",
        "Nur mit dem mitgelieferten Netzteil laden. Keine beschädigten Kabel verwenden.",
        "Bestimmungsgemäß verwenden. Vor Gebrauch Bedienungsanleitung lesen.",
    ],
}

CERTIFICATION_POOL = ["CE", "RoHS", "FCC", "REACH", "UKCA", "WEEE"]

# Real, publicly downloadable sample PDFs from sample-files.com — rotated
# per document type so generated fixtures reference URLs that actually
# resolve when the importer tries to download them.
SAFETY_DOCUMENT_POOL = {
    "user-manual": [
        "https://sample-files.com/downloads/documents/pdf/sample-20-page-pdf-a4-size.pdf",
        "https://sample-files.com/downloads/documents/pdf/sample-10-page-pdf-a4-size.pdf",
        "https://sample-files.com/downloads/documents/pdf/sample-5-page-pdf-a4-size.pdf",
    ],
    "declaration-of-conformity": [
        "https://sample-files.com/downloads/documents/pdf/sample-pdf-a4-size.pdf",
        "https://sample-files.com/downloads/documents/pdf/sample-pdf-a4-size-65kb.pdf",
        "https://sample-files.com/downloads/documents/pdf/basic-text.pdf",
    ],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def indent_xml(elem):
    raw = ET.tostring(elem, encoding="unicode")
    reparsed = minidom.parseString(raw)
    pretty = reparsed.toprettyxml(indent="    ")
    # Remove the extra <?xml...?> line minidom adds (we'll add our own)
    lines = pretty.split("\n")
    return "\n".join(lines[1:])


def child(parent, tag, text):
    """Add a child element with text content."""
    el = ET.SubElement(parent, tag)
    el.text = text
    return el


def slugify(text):
    return text.lower().replace(" ", "-").replace("'", "").replace("&", "and").replace("/", "-").replace("#", "").replace(",", "").strip("-")


def get_attr_set(subcategory):
    return ATTRIBUTE_SETS.get(subcategory, ATTRIBUTE_SETS.get(subcategory.split("-")[0], ATTRIBUTE_SETS["default"]))


def get_option_set(subcategory):
    return OPTION_SETS.get(subcategory, OPTION_SETS.get(subcategory.split("-")[0] + "-" + subcategory.split("-")[-1] if "-" in subcategory else subcategory, OPTION_SETS["default"]))


def make_variant_combinations(options, max_variants=6):
    """Generate up to max_variants combinations from option sets."""
    if not options:
        return [{}]
    combos = [{}]
    for opt_code, opt_name, values in options:
        new_combos = []
        for combo in combos:
            for val in values:
                new_combo = dict(combo)
                new_combo[opt_code] = (opt_name, val)
                new_combos.append(new_combo)
        combos = new_combos

    random.shuffle(combos)
    return combos[:max_variants]


def build_gpsr_party(parent_tag_name, party_data, parent):
    """Emit a GpsrPartyType element (<manufacturer> or <eu-responsible-person>)."""
    party = ET.SubElement(parent, parent_tag_name)
    child(party, "name", party_data["name"])
    if party_data.get("trademark"):
        child(party, "trademark", party_data["trademark"])
    child(party, "street",      party_data["street"])
    child(party, "city",        party_data["city"])
    child(party, "postal-code", party_data["postal-code"])
    child(party, "country",     party_data["country"])
    child(party, "email",       party_data["email"])
    if party_data.get("phone"):
        child(party, "phone", party_data["phone"])


def build_gpsr(manufacturer, sylius_code, idx, variant_count):
    """Build the <gpsr> block for the product, or None if no data available."""
    party_data = MANUFACTURER_GPSR.get(manufacturer)
    if not party_data:
        return None

    gpsr = ET.Element("gpsr")
    build_gpsr_party("manufacturer", party_data, gpsr)

    # EU responsible person required when the manufacturer is outside the EU.
    if party_data["country"] not in EU_COUNTRIES:
        build_gpsr_party("eu-responsible-person", DEFAULT_EU_REP, gpsr)

    # Model identifier — deterministic, derived from the Sylius code.
    child(gpsr, "model", f"MDL-{idx+1:05d}")

    # Safety notices — two locales, rotating through the notice pool so
    # fixtures exercise variety while remaining reproducible.
    notices = ET.SubElement(gpsr, "safety-notices")
    for locale, pool in SAFETY_NOTICE_POOL.items():
        n = ET.SubElement(notices, "notice")
        n.set("locale", locale)
        n.text = pool[idx % len(pool)]

    # Safety documents — user manual + DoC for every other product so that
    # both "with documents" and "without documents" shapes are covered.
    # URLs come from the real sample-files.com PDF pool so importer tests
    # can fetch them without stubbing.
    if idx % 2 == 0:
        manuals = SAFETY_DOCUMENT_POOL["user-manual"]
        docs_pool = SAFETY_DOCUMENT_POOL["declaration-of-conformity"]
        docs = ET.SubElement(gpsr, "safety-documents")
        for li, locale in enumerate(("en_US", "de_DE")):
            doc = ET.SubElement(docs, "document")
            doc.set("type", "user-manual")
            doc.set("locale", locale)
            child(doc, "url", manuals[(idx + li) % len(manuals)])
        doc = ET.SubElement(docs, "document")
        doc.set("type", "declaration-of-conformity")
        child(doc, "url", docs_pool[idx % len(docs_pool)])

    # Certifications — pick 1–3 from the pool based on idx.
    cert_count = 1 + (idx % 3)
    certs = ET.SubElement(gpsr, "certifications")
    for ci in range(cert_count):
        cert = ET.SubElement(certs, "certification")
        child(cert, "code", CERTIFICATION_POOL[(idx + ci) % len(CERTIFICATION_POOL)])

    return gpsr


# ── Product builder ───────────────────────────────────────────────────────────

def build_product(idx, total):
    template = PRODUCT_TEMPLATES[idx % len(PRODUCT_TEMPLATES)]
    name_tpl, main_cat, sub_cat, price_range, weight_range, manufacturer = template

    n = (idx // len(PRODUCT_TEMPLATES)) + 1
    name_en = name_tpl.format(n=n) if "{n}" in name_tpl else name_tpl

    base_price  = random.randint(*price_range)
    base_weight = round(random.uniform(*weight_range), 3)
    ext_code    = f"EXT-{idx+1:05d}"
    sylius_code = f"PROD-{idx+1:05d}"

    prod = ET.Element("product")
    prod.set("enabled", "true")
    child(prod, "code",          sylius_code)
    child(prod, "external-code", ext_code)
    child(prod, "manufacturer",  manufacturer)
    # For the generated fixtures, brand == manufacturer (the name is the
    # consumer-facing mark for these templates). Real imports may differ.
    child(prod, "brand",         manufacturer)

    # ── Translations
    translations = ET.SubElement(prod, "translations")

    tr_en = ET.SubElement(translations, "translation")
    tr_en.set("locale", "en_US")
    child(tr_en, "name",              name_en)
    child(tr_en, "slug",              slugify(f"{name_en}-{idx+1}"))
    child(tr_en, "short-description", f"{name_en} — high quality product.")
    child(tr_en, "description",       f"<p>Detailed description of {name_en}. Product index {idx+1} of {total}.</p>")
    child(tr_en, "meta-title",        f"{name_en} | Buy online")
    child(tr_en, "meta-description",  f"Buy {name_en} at the best price. Free shipping available.")

    de_name = f"{random.choice(DE_PREFIXES)} {name_en}"
    tr_de = ET.SubElement(translations, "translation")
    tr_de.set("locale", "de_DE")
    child(tr_de, "name", de_name)
    child(tr_de, "slug", slugify(f"{de_name}-{idx+1}"))

    fr_name = f"{name_en} {random.choice(FR_SUFFIXES)}"
    tr_fr = ET.SubElement(translations, "translation")
    tr_fr.set("locale", "fr_FR")
    child(tr_fr, "name", fr_name)
    child(tr_fr, "slug", slugify(f"{fr_name}-{idx+1}"))

    # ── Taxons
    cat_names = {code: name for code, _, name in CATEGORIES}
    taxons = ET.SubElement(prod, "taxons")
    taxons.set("main", sub_cat)
    for tax_code in (sub_cat, main_cat):
        t = ET.SubElement(taxons, "taxon")
        child(t, "code",          tax_code)
        child(t, "external-code", f"CAT-{tax_code.upper()}")
        child(t, "name",          cat_names.get(tax_code, tax_code))

    # ── Attributes
    attr_set = get_attr_set(sub_cat)
    if attr_set:
        attributes = ET.SubElement(prod, "attributes")
        for attr_code, attr_name, attr_values in attr_set:
            val = random.choice(attr_values)
            a = ET.SubElement(attributes, "attribute")
            child(a, "code",                attr_code)
            child(a, "name",                attr_name)
            child(a, "external-code",       f"ATTR-{attr_code.upper()}")
            child(a, "value",               val)
            child(a, "value-code",          slugify(val))
            child(a, "external-value-code", f"VAL-{slugify(val).upper()[:8]}")

    # ── Images (dummyimage.com placeholders so URLs actually resolve in tests)
    images = ET.SubElement(prod, "images")
    img_slug = slugify(name_en)
    for variant_tag, size, label in [
        ("main",       "800x600", "main"),
        ("additional", "800x600", "detail"),
        ("thumbnail",  "200x200", "thumb"),
    ]:
        img = ET.SubElement(images, "image")
        img.set("type", variant_tag)
        child(img, "url", f"https://dummyimage.com/{size}/cccccc/333333.jpg&text={img_slug}-{label}")

    # ── Variants
    option_set = get_option_set(sub_cat)
    max_variants = random.choice([2, 3, 4, 6])
    combos = make_variant_combinations(option_set, max_variants)

    variants = ET.SubElement(prod, "variants")
    for vi, combo in enumerate(combos):
        variant = ET.SubElement(variants, "variant")
        variant.set("enabled", "true")
        # condition — mostly new, occasionally used / refurbished
        variant.set("condition", random.choices(
            ["new", "used", "refurbished"],
            weights=[85, 8, 7],
        )[0])

        combo_slug = "-".join(slugify(v) for _, v in combo.values()) if combo else "default"
        child(variant, "code",          f"{sylius_code}-{combo_slug.upper()[:20]}")
        child(variant, "external-code", f"{ext_code}-{vi+1:02d}")
        # EAN is optional — roughly 70 % of variants have one
        if random.random() < 0.7:
            ean_base = 5900000000000 + (idx * 100) + vi
            child(variant, "ean", str(ean_base))

        # variant name = combination of values
        combo_label = " / ".join(v for _, v in combo.values()) if combo else name_en
        vtr = ET.SubElement(variant, "translation")
        vtr.set("locale", "en_US")
        child(vtr, "name", combo_label)
        child(vtr, "slug", slugify(f"{name_en}-{combo_label}-{idx+1}"))

        vtr_de = ET.SubElement(variant, "translation")
        vtr_de.set("locale", "de_DE")
        child(vtr_de, "name", combo_label)

        if combo:
            options_el = ET.SubElement(variant, "options")
            for opt_code, (opt_name, opt_val) in combo.items():
                o = ET.SubElement(options_el, "option")
                child(o, "code",                opt_code)
                child(o, "name",                opt_name)
                child(o, "external-code",       f"OPT-{opt_code.upper()}")
                child(o, "value",               opt_val)
                child(o, "value-code",          slugify(opt_val))
                child(o, "external-value-code", f"VAL-{slugify(opt_val).upper()[:8]}")

        # price increases slightly per variant
        variant_price = base_price + (vi * random.randint(500, 2000))
        vat_rate = random.choice([20, 21, 10, 5])
        vat_amount = int(round(variant_price * (1 + vat_rate / 100)))
        price_el = ET.SubElement(variant, "price")
        price_el.set("currency", "EUR")
        # Rotate through the three supported pricing shapes so test data exercises each one.
        price_shape = vi % 3
        if price_shape == 0:
            # Net price only
            price_el.set("amount", str(variant_price))
        elif price_shape == 1:
            # Gross price only — vat is required alongside vat-amount
            price_el.set("vat-amount", str(vat_amount))
            price_el.set("vat",        str(vat_rate))
        else:
            # Net + gross + vat
            price_el.set("amount",     str(variant_price))
            price_el.set("vat-amount", str(vat_amount))
            price_el.set("vat",        str(vat_rate))

        stock_el = ET.SubElement(variant, "stock")
        stock_el.set("on-hand", str(random.randint(0, 200)))

        dim_el = ET.SubElement(variant, "dimensions")
        dim_el.set("weight", str(round(base_weight + vi * 0.01, 3)))
        dim_el.set("width",  str(round(random.uniform(50, 300), 1)))
        dim_el.set("height", str(round(random.uniform(100, 400), 1)))
        dim_el.set("depth",  str(round(random.uniform(10, 150), 1)))

    # GPSR block — appended after <variants> per the XSD sequence.
    gpsr_el = build_gpsr(manufacturer, sylius_code, idx, len(combos))
    if gpsr_el is not None:
        prod.append(gpsr_el)

    return prod


# ── File builder ──────────────────────────────────────────────────────────────

def build_file(count, output_path, start_index=0, total=None):
    # start_index/total let manifest parts share a disjoint index range
    # (e.g. part-a: 0..249, part-b: 250..499) so product codes don't collide.
    if total is None:
        total = count

    root = ET.Element("sylius-import")
    root.set("version",        "2.0")
    root.set("default-locale", "en_US")
    root.set("channel",        "default")
    root.set("xmlns:xsi",      "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation",
             "https://elcuro.github.io/sylius-import-schema/sylius-import-2.0.xsd")

    products_el = ET.SubElement(root, "products")
    for i in range(count):
        products_el.append(build_product(start_index + i, total))

    xml_body = indent_xml(root)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<!-- Test import file: {count} products -->\n')
        f.write(xml_body)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"  {output_path}  ({count} products, {size_kb:.1f} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────

def build_manifest(files, output_path):
    root = ET.Element("sylius-import-manifest")
    root.set("version",   "2.0")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation",
             "https://elcuro.github.io/sylius-import-schema/sylius-import-2.0.xsd")

    # Mix forms so the fixture exercises both reference styles:
    # first entry as a relative path, remaining entries as absolute URLs.
    base_url = "https://elcuro.github.io/sylius-import-schema/tests"
    files_el = ET.SubElement(root, "files")
    for i, path in enumerate(files):
        name = os.path.basename(path)
        child(files_el, "file", name if i == 0 else f"{base_url}/{name}")

    xml_body = indent_xml(root)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write(xml_body)
    print(f"  {output_path}  (manifest for {len(files)} files)")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "tests")
    os.makedirs(out_dir, exist_ok=True)

    print("Generating test files...")
    counts = [3, 50, 100, 500]
    generated = []
    for count in counts:
        path = os.path.join(out_dir, f"test-{count}.xml")
        build_file(count, path)
        generated.append(path)

    # Manifest for the 500-product file split into two disjoint halves
    # (part-a covers products 1..250, part-b covers 251..500).
    half = 250
    path_a = os.path.join(out_dir, "test-500-part-a.xml")
    path_b = os.path.join(out_dir, "test-500-part-b.xml")
    build_file(half, path_a, start_index=0,    total=half * 2)
    build_file(half, path_b, start_index=half, total=half * 2)
    build_manifest([path_a, path_b], os.path.join(out_dir, "test-500-manifest.xml"))

    print("Done.")
