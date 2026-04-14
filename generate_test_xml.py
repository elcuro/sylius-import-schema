#!/usr/bin/env python3
"""
Generate test sylius-import XML files with realistic product data.
Produces: test-3.xml, test-50.xml, test-100.xml, test-500.xml
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import random
import math
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def indent_xml(elem):
    raw = ET.tostring(elem, encoding="unicode")
    reparsed = minidom.parseString(raw)
    pretty = reparsed.toprettyxml(indent="    ")
    # Remove the extra <?xml...?> line minidom adds (we'll add our own)
    lines = pretty.split("\n")
    return "\n".join(lines[1:])


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
    prod.set("code",          sylius_code)
    prod.set("external-code", ext_code)
    prod.set("enabled",       "true")
    prod.set("manufacturer",  manufacturer)

    # ── Translations
    translations = ET.SubElement(prod, "translations")

    tr_en = ET.SubElement(translations, "translation")
    tr_en.set("locale",            "en_US")
    tr_en.set("name",              name_en)
    tr_en.set("slug",              slugify(f"{name_en}-{idx+1}"))
    tr_en.set("short-description", f"{name_en} — high quality product.")
    tr_en.set("description",       f"&lt;p&gt;Detailed description of {name_en}. Product index {idx+1} of {total}.&lt;/p&gt;")
    tr_en.set("meta-title",        f"{name_en} | Buy online")
    tr_en.set("meta-description",  f"Buy {name_en} at the best price. Free shipping available.")

    de_name = f"{random.choice(DE_PREFIXES)} {name_en}"
    tr_de = ET.SubElement(translations, "translation")
    tr_de.set("locale", "de_DE")
    tr_de.set("name",   de_name)
    tr_de.set("slug",   slugify(f"{de_name}-{idx+1}"))

    fr_name = f"{name_en} {random.choice(FR_SUFFIXES)}"
    tr_fr = ET.SubElement(translations, "translation")
    tr_fr.set("locale", "fr_FR")
    tr_fr.set("name",   fr_name)
    tr_fr.set("slug",   slugify(f"{fr_name}-{idx+1}"))

    # ── Taxons
    taxons = ET.SubElement(prod, "taxons")
    taxons.set("main", sub_cat)
    t1 = ET.SubElement(taxons, "taxon"); t1.set("code", sub_cat)
    t2 = ET.SubElement(taxons, "taxon"); t2.set("code", main_cat)

    # ── Attributes
    attr_set = get_attr_set(sub_cat)
    if attr_set:
        attributes = ET.SubElement(prod, "attributes")
        for attr_code, attr_name, attr_values in attr_set:
            val = random.choice(attr_values)
            a = ET.SubElement(attributes, "attribute")
            a.set("code",          attr_code)
            a.set("name",          attr_name)
            a.set("external-code", f"ATTR-{attr_code.upper()}")
            a.set("value",         val)
            a.set("value-code",    slugify(val))
            a.set("external-value-code", f"VAL-{slugify(val).upper()[:8]}")

    # ── Images
    images = ET.SubElement(prod, "images")
    img_slug = slugify(name_en)
    i1 = ET.SubElement(images, "image")
    i1.set("url",  f"https://cdn.example.com/{img_slug}/main.jpg")
    i1.set("type", "main")
    i2 = ET.SubElement(images, "image")
    i2.set("url",  f"https://cdn.example.com/{img_slug}/detail.jpg")
    i2.set("type", "additional")
    i3 = ET.SubElement(images, "image")
    i3.set("url",  f"https://cdn.example.com/{img_slug}/thumb.jpg")
    i3.set("type", "thumbnail")

    # ── Variants
    option_set = get_option_set(sub_cat)
    max_variants = random.choice([2, 3, 4, 6])
    combos = make_variant_combinations(option_set, max_variants)

    variants = ET.SubElement(prod, "variants")
    for vi, combo in enumerate(combos):
        variant = ET.SubElement(variants, "variant")
        combo_slug = "-".join(slugify(v) for _, v in combo.values()) if combo else "default"
        variant.set("code",          f"{sylius_code}-{combo_slug.upper()[:20]}")
        variant.set("external-code", f"{ext_code}-{vi+1:02d}")
        variant.set("enabled",       "true")
        # EAN is optional — roughly 70 % of variants have one
        if random.random() < 0.7:
            ean_base = 5900000000000 + (idx * 100) + vi
            variant.set("ean", str(ean_base))

        # variant name = combination of values
        combo_label = " / ".join(v for _, v in combo.values()) if combo else name_en
        vtr = ET.SubElement(variant, "translation")
        vtr.set("locale", "en_US")
        vtr.set("name",   combo_label)
        vtr.set("slug",   slugify(f"{name_en}-{combo_label}-{idx+1}"))

        vtr_de = ET.SubElement(variant, "translation")
        vtr_de.set("locale", "de_DE")
        vtr_de.set("name",   combo_label)

        if combo:
            options_el = ET.SubElement(variant, "options")
            for opt_code, (opt_name, opt_val) in combo.items():
                o = ET.SubElement(options_el, "option")
                o.set("code",                opt_code)
                o.set("name",                opt_name)
                o.set("external-code",       f"OPT-{opt_code.upper()}")
                o.set("value",               opt_val)
                o.set("value-code",          slugify(opt_val))
                o.set("external-value-code", f"VAL-{slugify(opt_val).upper()[:8]}")

        # price increases slightly per variant
        variant_price = base_price + (vi * random.randint(500, 2000))
        price_el = ET.SubElement(variant, "price")
        price_el.set("currency", "EUR")
        price_el.set("amount",   str(variant_price))

        stock_el = ET.SubElement(variant, "stock")
        stock_el.set("on-hand", str(random.randint(0, 200)))

        dim_el = ET.SubElement(variant, "dimensions")
        dim_el.set("weight", str(round(base_weight + vi * 0.01, 3)))
        dim_el.set("width",  str(round(random.uniform(50, 300), 1)))
        dim_el.set("height", str(round(random.uniform(100, 400), 1)))
        dim_el.set("depth",  str(round(random.uniform(10, 150), 1)))

    return prod


# ── File builder ──────────────────────────────────────────────────────────────

def build_file(count, output_path):
    root = ET.Element("sylius-import")
    root.set("version",        "2.0")
    root.set("default-locale", "en_US")
    root.set("channel",        "default")
    root.set("xmlns:xsi",      "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation",
             "https://elcuro.github.io/sylius-import-schema/sylius-import-2.0.xsd")

    products_el = ET.SubElement(root, "products")
    for i in range(count):
        products_el.append(build_product(i, count))

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

    files_el = ET.SubElement(root, "files")
    for path in files:
        f = ET.SubElement(files_el, "file")
        f.set("path", os.path.basename(path))

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

    # Manifest for the 500-product file split into two halves
    half = 250
    path_a = os.path.join(out_dir, "test-500-part-a.xml")
    path_b = os.path.join(out_dir, "test-500-part-b.xml")
    build_file(half, path_a)
    build_file(half, path_b)
    build_manifest([path_a, path_b], os.path.join(out_dir, "test-500-manifest.xml"))

    print("Done.")
