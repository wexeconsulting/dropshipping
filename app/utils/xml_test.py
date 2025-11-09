import unittest
import xml.etree.ElementTree as ET
import io
import sys
from utils.logger import get_technical_logger

logger = get_technical_logger(__name__)

class TestXMLStructure(unittest.TestCase):
    def setUp(self):
        # Paths to the XML files to be tested
        self.xml_files = ["xml_result_1.xml"]
        
        # Expected structure (tag names)
        self.expected_tags = {
            "manufacturer_name", "name", "ean", "category_name",
            "quantity", "price", "tax_rate", "image"
        } | {f"image_extra_{i}" for i in range(1, 16)} | {"description"}

    def test_xml_structure(self):
        for xml_file in self.xml_files:
            with self.subTest(xml_file=xml_file):
                logger.info(f"Testing file: {xml_file}")
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Ensure root is <products>
                self.assertEqual(root.tag, "products", "Root element should be <products>")
                logger.debug(f"Root element: {root.tag}")
                
                elem_correct1 = 0
                elem_correct2 = 0

                # Check each <product> element
                for product in root.findall("product"):
                    tags = {child.tag for child in product}
                    #logger.debug(f"Product tags: {tags}")

                    # Check if all expected tags are present
                    self.assertTrue(self.expected_tags.issubset(tags), "Some expected tags are missing")
                    elem_correct1 += 1
                    
                    # Check if there are no unexpected tags
                    self.assertTrue(tags.issubset(self.expected_tags), "Unexpected tags found in XML")
                    elem_correct2 += 1
                logger.info(f"Correct elements (all expected tags): {elem_correct1}")
                logger.info(f"Correct elements (no unexpected tags): {elem_correct2}")

def run_tests():
    """Run the XML structure test and return the results as a string."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestXMLStructure)
    buffer = io.StringIO()  
    runner = unittest.TextTestRunner(stream=buffer, verbosity=2)
    result = runner.run(suite)
    return buffer.getvalue()

if __name__ == "__main__":
    unittest.main()
