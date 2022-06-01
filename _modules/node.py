import os, sys

from pprint import pprint

from string_helpers import *
from path import *

node_ignore_list = ["Documents and Settings", "System Volume Information", "$RECYCLE.BIN", "$Recycle.Bin"]

class Node:
    
    def __init__(self, path=None, parent_node=None):
        
        self.name   = ""
        self.path   = ""
        self.type   = ""
        self.parent = parent_node
        
        if path is not None:
            filepath = Path(path)
            
            self.name = filepath.name
            self.path = filepath.path
            self.type = filepath.type
            
            if self.type == "Folder":
                self.children = []
                self.walk()
            elif self.type == "File":
                self.name      = filepath.name
                self.name_ext  = filepath.name_ext
                self.extension = filepath.extension
    
    def walk(self):
        items = os.listdir(self.path)
        if len(items) > 0:
            for item in items:
                if item not in node_ignore_list:
                    child = Node(self.path + "\\" + item, self)
                    self.children.append(child)
    
    def rewalk(self):
        if self.type == "Folder":
            self.children.clear()
            self.walk()
    
    def rename(self, new_name=""):
        if new_name:
            if self.parent:
                new_path = self.parent.path + "\\" + new_name
            else:
                new_path = Path(self.path).parent().path + "\\" + new_name
            if self.type == "File":
                file_name = filename(new_name)
                # pprint(file_name)
                self.name      = file_name["name"]
                self.extension = file_name["extension"]
                self.name_ext  = file_name["name_ext"]
            elif self.type == "Folder":
                self.name = new_name
            os.rename(self.path, new_path)
            self.path = new_path
            self.rewalk()
    
    def get_children(self, name=None, type=None, extensions=None, deep=False, children=None):
        if children is None:
            children = []
        if self.type == "Folder":
            for child in self.children:
                if extensions is not None and child.type == "File":
                    if name is not None:
                        if child.name == name and child.extension in extensions:
                            children.append(child)
                    else:
                        if child.extension.lower() in extensions:
                            children.append(child)
                else:
                    if name is not None:
                        if type is not None:
                            if child.name == name and child.type == type:
                                children.append(child)
                        else:
                            if child.name == name:
                                children.append(child)
                    elif type is not None:
                        if child.type == type:
                            children.append(child)
        
                if deep is True:
                    child.get_children(name, type, extensions, deep, children);
        return children
    
    def get_size(self, total_size=None):
        if total_size is None:
            total_size = 0
        if self.type == "File":
            total_size += int(os.path.getsize(self.path))
        elif self.type == "Folder":
            for item in self.children:
                total_size = item.get_size(total_size)
        return total_size
    
    def build_path(self, path_built=None):
        if path_built is None:
            path_built = []
        path_built.append(self.name)
        if self.parent is None:
            path_built.pop()
            path_built.append(self.path)
        else:
            self.parent.build_path(path_built)
        return "\\".join(reversed(path_built))
    
    def dump(self, indent=0, deep=True):
        
        field_length = 0
        children_count = 0
        
        if self.type == "File":
            field_length = 12
        else:
            field_length = 7
            children_count = len(self.children)
            if children_count > 0:
                field_length = 9
        
        print(tabspace(indent) + "object(" + type(self).__name__ + ") [")
        
        print(tabspace(indent + 1) + str_pad_right("type", field_length, " ") + ": " + str_quote(self.type))
        print(tabspace(indent + 1) + str_pad_right("name", field_length, " ") + ": " + str_quote(self.name))
        
        if self.type == "File":
            print(tabspace(indent + 1) + str_pad_right("name_ext", field_length, " ") + ": " + str_quote(self.name_ext))
            print(tabspace(indent + 1) + str_pad_right("extension", field_length, " ") + ": " + str_quote(self.extension))
            
        print(tabspace(indent + 1) + str_pad_right("path", field_length, " ") + ": " + str_quote(self.path))
        
        if isinstance(self.parent, Node):
            print(tabspace(indent + 1) + str_pad_right("parent", field_length, " ") + ": object(Node) { name : " + str_quote(self.parent.name) +" }")
        else:
            print(tabspace(indent + 1) + str_pad_right("parent", field_length, " ") + ": " + "None")
        
        if children_count > 0:
            if deep:
                print(tabspace(indent + 1) + str_pad_right("children", field_length, " ") + ": (" + str(children_count) + ") [")
                for item in self.children:
                    item.dump(indent + 2, deep)
                print(tabspace(indent + 1) + "]")
            else:
                print(tabspace(indent + 1) + str_pad_right("children", field_length, " ") + ": list(" + str(children_count) + ")")
                
        print(tabspace(indent) + "]")
