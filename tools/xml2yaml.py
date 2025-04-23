import xml.etree.ElementTree as ET
from typing import Dict, Any

try:
    import xmltodict
    import yaml
except ImportError:
    print("Install the optional dependencies [xml2yaml]")

def xml_to_dict(element: ET.Element) -> Dict[str, Any]:
    """Convert XML element to dictionary with attributes."""
    result = {}

    # Handle attributes
    if element.attrib:
        result.update(element.attrib)

    # Handle child elements
    children = list(element)
    if children:
        child_dict = {}
        for child in children:
            child_name = child.tag
            child_content = xml_to_dict(child)

            if child_name in child_dict:
                if not isinstance(child_dict[child_name], list):
                    child_dict[child_name] = [child_dict[child_name]]
                child_dict[child_name].append(child_content)
            else:
                # For elements that commonly appear multiple times, always start as a list
                if child_name in ['View', 'Choice', 'Image']:
                    child_dict[child_name] = [child_content]
                else:
                    child_dict[child_name] = child_content

        # If there are any children, store them directly under the parent
        for key, value in child_dict.items():
            result[key] = value

    return result


def dict_to_xml(data: Dict[str, Any], tag_name: str) -> ET.Element:
    """Convert dictionary to XML element."""
    element = ET.Element(tag_name)

    for key, value in data.items():
        if isinstance(value, list):
            # Handle lists of elements
            for item in value:
                child = dict_to_xml(item, key)
                element.append(child)
        elif isinstance(value, dict):
            # Handle single nested element
            child = dict_to_xml(value, key)
            element.append(child)
        else:
            # Handle attributes
            element.set(key, str(value))

    return element


def xml_to_yaml(xml_string: str) -> str:
    """Convert XML string to YAML string."""
    return yaml.dump(xmltodict.parse(xml_string))


def yaml_to_xml(yaml_string: str) -> str:
    """Convert YAML string to XML string."""
    data = yaml.safe_load(yaml_string)
    return xmltodict.unparse(data)

if __name__ == "__main__":
    # Test with input
    xml_input = '''<View>
        <View>
            <Header value="Choose a relevance class for the text"/>
            <HyperText name="post_text" value="$post_text"/>
            <Choices name="text_relevant" toName="post_text" choice="single" showInline="true">
                <Choice value="Relevant"/>
                <Choice value="Uncertain"/>
                <Choice value="Not relevant"/>
            </Choices>
        </View>
        <!-- Rest of your XML -->
    </View>'''

    # Convert XML to YAML
    yaml_output = xml_to_yaml(xml_input)
    print("XML to YAML:")
    print(yaml_output)