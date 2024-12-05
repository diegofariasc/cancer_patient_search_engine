from xml.etree.ElementTree import Element


def find_all_elements_by_atom_xpath(element: Element, field_name: str) -> list[Element]:
    return element.findall("{http://www.w3.org/2005/Atom}" + field_name)


def find_element_by_atom_xpath(element: Element, field_name: str) -> Element:
    return element.find("{http://www.w3.org/2005/Atom}" + field_name)


def find_elements_by_atom_xpath(
    element: Element, field_names: list[str]
) -> dict[str, Element]:
    return {
        field_name: find_element_by_atom_xpath(element, field_name)
        for field_name in field_names
    }
