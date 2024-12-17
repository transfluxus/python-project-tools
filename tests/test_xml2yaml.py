
from tools.env_root import root
from tools.xml2yaml import xml_to_yaml, yaml_to_xml

tests_dir = root(".") / "data/tests/"
test_path = (tests_dir / "xml2yaml")
test_path.mkdir(exist_ok=True)

def test_xml_to_yaml():
    output_yaml = xml_to_yaml((test_path / "in.xml").read_text())
    (test_path / "out.yaml").write_text(output_yaml)

def test_yaml_to_xml():
    output_xml = yaml_to_xml((test_path / "out.yaml").read_text())
    (test_path / "in_round.xml").write_text(output_xml)