import os

"""
Dependencies:
    tabspace()
    str_pad_right()
    str_quote()
    eol()
"""

class Path():
    
    def __init__(self, path=None):
        self.name   = ""
        self.path   = ""
        self.type   = ""
        # self.extension = None
        # self.name_ext = None
        # self.sep = None
        if path is not None:
            self.path = path
            self.parse(path)
        
    def parse(self, path):
        
        dirs = []
        
        if "\\" in path:
            self.sep  = "\\"
            dirs = path.split("\\")
        elif "/" in path:
            self.sep  = "/"
            dirs = path.split("/")
        
        if "\\" in path or "/" in path:
            self.name = dirs[-1]
        
        if os.path.isdir(path):
            self.type = "Folder"
            if hasattr(self, "sep") is False:
                self.sep = ""
            
        elif os.path.isfile(path):
            
            self.type = "File"
            
            if "." in self.name:
                fn = self.name.split(".")
                self.extension = fn.pop()
                
                if len(fn) > 1:
                    fn = ".".join(fn)
                else:
                    fn = "".join(fn)
                
                self.name_ext = self.name
                
                if fn == "":
                    self.name      = "." + self.extension
                    self.name_ext  = self.name
                    self.extension = ""
                else:
                    self.name = fn
            else:
                self.name_ext  = self.name
                self.extension = ""
    
    def get_parent_path(self):
        dirs = self.path.split(self.sep)
        dirs.pop()
        return Path(self.sep.join(dirs))
    
    def __str__(self):
        
        string = ""
        
        field_length = 0
        
        if self.type == "File":
            field_length = 10
        else:
            field_length = 5
        
        string += "object(" + type(self).__name__ + ") [" + eol()
        string += tabspace(1) + str_pad_right("name", field_length, " ") + ": " + str_quote(self.name) + eol()
        
        if hasattr(self, "extension"):
            string += tabspace(1) + str_pad_right("name_ext", field_length, " ") + ": " + str_quote(self.name_ext) + eol()
            string += tabspace(1) + str_pad_right("extension", field_length, " ") + ": " + str_quote(self.extension) + eol()
        
        string += tabspace(1) + str_pad_right("path", field_length, " ") + ": " + str_quote(self.path) + eol()
        string += tabspace(1) + str_pad_right("sep", field_length, " ") + ": " + str_quote(self.sep) + eol()
        
        string += tabspace(1) + str_pad_right("type", field_length, " ") + ": " + str_quote(self.type) + eol()
            
        string += "]"
        
        return string
    
    def dump(self):
        print(self)