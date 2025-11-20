import os
import xml.etree.ElementTree as ET

class DiagramObject:
    def __init__(self, obj_type, bounds, difficult, truncated):
        self.obj_type = obj_type
        self.bounds = bounds  #tuple
        self.difficult = difficult
        self.truncated = truncated

    @property
    def width(self):
        return self.bounds[2] - self.bounds[0] #xmax-xmin

    @property
    def height(self):
        return self.bounds[3] - self.bounds[1] #ymax-ymin

    @property
    def area(self):
        return self.width * self.height

    def __str__(self):
        return f"Type: {self.obj_type}   xmin, ymin, xmax, ymax: {self.bounds}   Width: {self.width}   Height: {self.height}   Area: {self.area}   Difficult: {self.difficult}   Truncated: {self.truncated}"

class Diagram:
    def __init__(self, filename, size, objects):
        self.filename = filename
        self.size = size  #(width, height, depth)
        self.objects = objects  #list of DiagramObject instances

    @property
    def dimension(self):
        return self.size[0] * self.size[1] #width*height
    
    @property
    def dwidth(self):
        return self.size[0] 
    
    @property
    def dheight(self):
        return self.size[1]

    def __str__(self):
        obj_details = ""
        for obj in self.objects:
            obj_details += str(obj) + "\n"
        without_suffix = self.filename.rsplit('.', 1)
        self.filename = without_suffix[0]
        return f"Diagram: {self.filename}   Size: {self.size}   Area: {self.dimension}\nObjects:\n{obj_details}"

diagrams = {} #contains file name as key and Diagram.__str__

def list_xml_files(directory):
    xml_files = [] 
    files = os.listdir(directory)  #gets all files and folders in directory
    
    for f in files:  
        if f.lower().endswith('.xml'): 
            xml_files.append(f)  #only add XML file to list
    
    return xml_files

def load_diagram(file_path):
   
    filename = os.path.basename(file_path)  #extract filename from path
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        without_suffix = filename.rsplit('.', 1)  #split only at last .
        if len(without_suffix) < 2 or without_suffix[1].lower() != "xml":
            print(f"Error loading file '{filename.upper()}'. Invalid filename or file not found.")
            return

        if without_suffix[0] in diagrams:
            print(f"Error: Diagram '{without_suffix[0]}' is already loaded.")
            return
        
        width = int(root.find("size/width").text)
        height = int(root.find("size/height").text)
        depth = int(root.find("size/depth").text)
        size = (width, height, depth)
        
        objects = []
        for obj in root.findall("object"):
            obj_type = obj.find("name").text
            bndbox = obj.find("bndbox")
            xmin = int(bndbox.find("xmin").text)
            ymin = int(bndbox.find("ymin").text)
            xmax = int(bndbox.find("xmax").text)
            ymax = int(bndbox.find("ymax").text)
            difficult = bool(int(obj.find("difficult").text)) #0 for false, 1 for true
            truncated = bool(int(obj.find("truncated").text))
            objects.append(DiagramObject(obj_type, (xmin, ymin, xmax, ymax), difficult, truncated))
        diagrams[without_suffix[0]] = Diagram(filename, size, objects)

        print(f"Diagram '{without_suffix[0]}' was successfully loaded.")
    except Exception as e:
        print(f"Error loading file '{filename.upper()}'. Invalid filename or file not found.")

            
def list_diagrams():
    if diagrams:
        print(f"{len(diagrams)} diagrams loaded: ")
        for name in diagrams:
            print(f"'{name}'")
        print(".")
    else:
        print("0 diagrams loaded.")

def display_diagram_info():
    name = input("Enter diagram name: ")
    if name.lower().endswith('.xml'): 
        new_name = name.rsplit('.', 1)
        name = new_name[0]

    diagram = diagrams.get(name)
    if diagram:
        print(diagram)
    else:
        print("Diagram not found.")

def find_by_type():
    obj_type = input("Enter the diagram type: ").lower()
    
    found = []  #store diagram names with matches

    for name, diagram in diagrams.items():  
        for obj in diagram.objects: 
            if obj.obj_type.lower() == obj_type:  
                found.append(name)  
                break  #one object in this diagram means there is a match

    if found:
        print(f"Found {len(found)} diagram(s):")
        print("\n".join(found))
    else:
        print("No diagrams found.")

def find_by_dimension():
    try:
        min_width = input("Min width (enter blank for zero): ").strip() #without strip can be true if string is a space
        max_width = input("Max width (enter blank for max): ").strip()
        min_height = input("Min height (enter blank for zero): ").strip()
        max_height = input("Max height (enter blank for max): ").strip()
        difficult = input("Difficult (yes/no/All): ").strip().lower() or "all"
        truncated = input("Truncated (yes/no/All): ").strip().lower() or "all"
        
        #convert input values to integers
        if min_width:  #not empty string
            min_width = int(min_width)  
        else:  
            min_width = 0  #no value is entered  

        if max_width:  
            max_width = int(max_width)  
        else:  
            max_width = float('inf')  #infinity if no value is entered  

        if min_height:  
            min_height = int(min_height)  
        else:  
            min_height = 0 

        if max_height:  
            max_height = int(max_height)  
        else:  
            max_height = float('inf')  


        if difficult == "y" or difficult == "yes":  
            difficult = True  
        elif difficult == "n" or difficult == "no":  
            difficult = False  
        else:  
            difficult = None  #blank or all 

        if truncated == "y" or truncated == "yes":  
            truncated = True  
        elif truncated == "n" or truncated == "no":  
            truncated = False  
        else:  
            truncated = None 
        
        found = []
        for name, d in diagrams.items():
            if min_width <= d.dwidth and max_width >= d.dwidth and min_height <= d.dheight and max_height >= d.dheight:
                is_difficult = any(o.difficult == True for o in d.objects) #one object is diificult
                is_truncated = any(o.truncated == True for o in d.objects) 

                not_difficult = all(o.difficult == False for o in d.objects)  #all objects are not difficult
                not_truncated = all(o.truncated == False for o in d.objects)  

                if difficult is None or (difficult == True and is_difficult == True) or (difficult == False and not_difficult == True):
                    if truncated is None or (truncated == True and is_truncated == True) or (truncated == False and not_truncated == True):
                        found.append(name)
        
        if found:
            print(f"Found {len(found)} diagram(s):")
            print("\n".join(found))
        else:
            print("No diagrams found.")
    except Exception as e:
        print("Invalid input.")

def statistics():
    print(f"Number of loaded diagrams: {len(diagrams)}")

    total_objects = 0  
    for diagram in diagrams.values():  
        total_objects += len(diagram.objects) 
    
    print(f"Total number of total objects: {total_objects}")
    
    object_types = set()  
    for diagram in diagrams.values():  
        for obj in diagram.objects: 
            object_types.add(obj.obj_type) 
    
    print(f"Diagram Object Types: {', '.join(object_types)}")
    
    heights = []  
    widths = []
    areas = []  
    for diagram in diagrams.values():  
        heights.append(diagram.dheight)
        widths.append(diagram.dwidth)
        for obj in diagram.objects:
            areas.append(obj.area)

    if heights and widths:
        print(f"Minimum height of diagrams: {min(heights)}\nMaximum height of diagrams: {max(heights)}")
        print(f"Miniimum width of diagrams: {min(widths)}\nMaximum width of diagrams: {max(widths)}")
    if areas:
        print(f"Minimum object area: {min(areas)}\nMaximum object area: {max(areas)}\n")

def main(directory):
    while True:
        print("\n1. List Current Files\n2. List Diagrams\n3. Load File\n4. Display Diagram Info\n5. Search\n   5.1.  Find by type\n   5.2.  Find by dimension\n6. Statistics\n7. Exit")
        choice = input("Enter choice: ")
        
        if choice == "1":
            print("XML Files:", list_xml_files(directory))
        elif choice == "2":
            list_diagrams()
        elif choice == "3":
            filename = input("Enter filename: ")
            load_diagram(os.path.join(directory, filename))
        elif choice == "4":
            display_diagram_info()
        elif choice == "5":
            sub_choice = input("Select 5.1 or 5.2: ")
            if sub_choice == "5.1":
                find_by_type()
            elif sub_choice == "5.2":
                find_by_dimension()
        elif choice == "5.1":
            find_by_type()
        elif choice == "5.2":
            find_by_dimension()
        elif choice == "6":
            statistics()
        elif choice == "7":
            quitchoice = input("Are you sure you want to quit the program (yes/No)? ").strip().lower()
            if quitchoice == "y" or quitchoice == "yes":
                print("Good bye...")
                break
        else:
            print("Invalid number for choice")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("please type: Python3 <your_code.py> </.../test_path_to_xml_folder/>")
        sys.exit(1)
    main(sys.argv[1])
