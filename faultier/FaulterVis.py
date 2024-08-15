from IPython.display import HTML
import xml.etree.ElementTree as ET
import tempfile
import os
import urllib

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))

def update_text_fill(text_element, new_fill_color):
    """
    Updates the "fill" property of an SVG text element's style attribute.

    Args:
    text_element (ET.Element): The SVG text element to modify.
    new_fill_color (str): The new color to set for the fill property.
    """
    # Check if the element has a 'style' attribute
    if 'style' in text_element.attrib:
        # Split the style attribute into individual properties
        styles = text_element.get('style').split(';')
        new_styles = []
        fill_updated = False
        for style in styles:
            if style.strip().startswith('fill:'):
                # Update the fill color
                new_styles.append(f'fill:{new_fill_color}')
                fill_updated = True
            else:
                new_styles.append(style)
        if not fill_updated:
            # If fill was not previously set, add it
            new_styles.append(f'fill:{new_fill_color}')
        # Update the style attribute
        text_element.set('style', ';'.join(new_styles))
    else:
        # If there's no style attribute, simply add one with the fill color
        text_element.set('style', f'fill:{new_fill_color}')


class FaultierVis:
    def __init__(self, svg_file_path):
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
         # Parse the SVG file
        tree = ET.parse(svg_file_path)
        self.root = tree.getroot()

        # SVG files have namespaces, so we need to handle them.
        self.namespaces = {'svg': 'http://www.w3.org/2000/svg'}

    def change_fill(self, group_id, fill):
        g_element = self.root.find(f".//*[@id='{group_id}']", self.namespaces)

        if g_element is not None:
            # Find the 'text' element within the 'g' element. Assuming it's the first 'text' element for simplicity.
            text_element = g_element.find('.//svg:text', self.namespaces)
            
            if text_element is not None:
                update_text_fill(text_element, fill)
            else:
                print(f"No 'text' element found within the group '{group_id}'.")
                return None
        else:
            print(f"No element with ID '{group_id}' found in the SVG file.")
            return None

    def replace_text(self, group_id, text, fill=None):
        # Find the 'g' element by ID
        g_element = self.root.find(f".//*[@id='{group_id}']", self.namespaces)

        if g_element is not None:
            # Find the 'text' element within the 'g' element. Assuming it's the first 'text' element for simplicity.
            text_element = g_element.find('.//svg:text', self.namespaces)
            
            if text_element is not None:
                # Update the entire text content directly if you want to replace everything inside <text>
                text_element.text = text

                # Optionally, clear existing tspan elements (if you want to remove them)
                for tspan in text_element.findall('.//svg:tspan', self.namespaces):
                    text_element.remove(tspan)

                if fill:
                    update_text_fill(text_element, fill)

                # Convert the updated SVG tree back to a string
                svg_string = ET.tostring(self.root, encoding='unicode')

                # Optionally, strip out the xml declaration if present
                # svg_string = svg_string.replace('<?xml version=\'1.0\' encoding=\'unicode\'?>', '')

                return svg_string
            else:
                print(f"No 'text' element found within the group '{group_id}'.")
                return None
        else:
            print(f"No element with ID '{group_id}' found in the SVG file.")
            return None   


    def create_tag(self):
        # fd, path = tempfile.mkstemp(suffix=".svg", text=True)
        # f = os.fdopen(fd, 'w')
        # print(f)
        svg_string = ET.tostring(self.root, encoding='unicode')

        # URL-encode the SVG string
        encoded_svg = urllib.parse.quote(svg_string)

        # Create the <img> tag with the encoded SVG as the src
        img_tag = f'<img width=800 src="data:image/svg+xml,{encoded_svg}" alt="Inline SVG" />'

        return img_tag

    def show(self):
        display(HTML(self.create_tag()))

    @staticmethod
    def show_stm32_glitch_configuration():
        fv = FaultierVis(MODULE_DIR + "/docs/topview.svg")
        fv.replace_text("text_crowbar", "To STM32 VCore")
        fv.replace_text("text_mux0", "To STM32 VCC")
        fv.replace_text("text_ext0", "To STM32 RST")
        fv.replace_text("text_ext1", "Unused", fill="#999")
        fv.show()
        fv = FaultierVis(MODULE_DIR + "/docs/sideview.svg")
        fv.change_fill("text_swd_vcc", "#555")
        for i in range(0, 10):
            fv.change_fill(f"text_io{i}", "#555")
        for i in range(1, 3):
            fv.change_fill(f"text_m{i}_out", "#555")
            fv.change_fill(f"text_m{i}_in0", "#555")
            fv.change_fill(f"text_m{i}_in1", "#555")
        fv.change_fill(f"text_5v", "#555")
        # fv.replace_text(f"text_3.3v", "3.3V", "#555")
        fv.change_fill(f"text_gnd_top", "#555")
        fv.change_fill(f"text_gnd_bottom", "#555")
        # fv.replace_text("text_mux0", "To STM32 VCC")
        # fv.replace_text("text_ext0", "Unused", fill="#999")
        # fv.replace_text("text_ext1", "Unused", fill="#999")
        fv.show()
    
    @staticmethod
    def show_nrf52_glitch_configuration():
        fv = FaultierVis(MODULE_DIR + "/docs/topview.svg")
        fv.replace_text("text_crowbar", "To nRF52 VCore")
        fv.replace_text("text_mux0", "To nRF52 VCC")
        fv.replace_text("text_ext0", "Unused", fill="#999")
        fv.replace_text("text_ext1", "Unused", fill="#999")
        fv.show()
        fv = FaultierVis(MODULE_DIR + "/docs/sideview.svg")
        fv.change_fill("text_swd_vcc", "#555")
        for i in range(0, 10):
            fv.change_fill(f"text_io{i}", "#555")
        for i in range(1, 3):
            fv.change_fill(f"text_m{i}_out", "#555")
            fv.change_fill(f"text_m{i}_in0", "#555")
            fv.change_fill(f"text_m{i}_in1", "#555")
        fv.change_fill(f"text_5v", "#555")
        # fv.replace_text(f"text_3.3v", "3.3V", "#555")
        fv.change_fill(f"text_gnd_top", "#555")
        fv.change_fill(f"text_gnd_bottom", "#555")
        # fv.replace_text("text_mux0", "To STM32 VCC")
        # fv.replace_text("text_ext0", "Unused", fill="#999")
        # fv.replace_text("text_ext1", "Unused", fill="#999")
        fv.show()
