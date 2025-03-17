import xml.etree.ElementTree as ET
import pandas as pd

def parse_xml_to_dict(xml_content, mapping):
    root = ET.fromstring(xml_content)
    result = []
    products = root.findall(mapping["product_index"])
    for product in products:
        product_data = {}
        for key, tag in mapping["fields"].items():
            # handle elements defined as collection to flat structure
            if isinstance(tag, dict):  
                elements = product.findall(tag["collection"])
                for idx, element in enumerate(elements):
                    if idx == tag["maxMappedElems"]:
                        break
                    if idx == 0:
                        product_data[tag["firstElem"]] = element.text.strip() if element is not None and element.text else None
                    else:
                        product_data[f"{tag['prefix']}{idx}"] = element.text.strip() if element is not None and element.text else None
            # otherwise maps directly
            else:
                element = product.find(tag)
                product_data[key] = element.text.strip() if element is not None and element.text else None
        if not product_data["quantity"]:
            continue
        result.append(product_data)

    return result

def parse_df_to_result_xml(df):
    root = ET.Element("products")
    for _, row in df.iterrows():
        product_elem = ET.SubElement(root, "product")
        for key, value in row.items():
            elem = ET.SubElement(product_elem, key)
            if pd.notna(value):
                if key in ["manufacturer_name", "name", "category_name", "description", "image", "image_extra_1", "image_extra_2", "image_extra_3", "image_extra_4", "image_extra_5", "image_extra_6", "image_extra_7", "image_extra_8"]:
                    elem.text = f'<![CDATA[{value}]]>'
                else:
                    elem.text = str(value)
            else:
                elem.text = ""
    xml_declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml_str = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
    # Replace escaped CDATA
    xml_str = xml_str.replace('&lt;![CDATA[', '<![CDATA[').replace(']]&gt;', ']]>')
    return xml_declaration + xml_str
