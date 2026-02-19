# Memory constraints? What do we do if we hit it 
# Overwrite if already exists?
# COnflicting names

class File:
    def __init__(self, name, content):
        self.name = name
        self.content = None
        # Save each version of the file or have it be just the delta from the previous version. 
        # This reduces the duplication of information.
        # Tradeoff is that recreating from the versions will require us to parse all of the different versions.
        self.versions = []

class Directory: 
    def __init__(self, name):
        self.name = name
        self.subdirectories = {}
        self.files = {}
        
    def __str__(self):
        return f'''
            Directory name: {self.name}
            subdirectories: {self.subdirectories.items()}
            files: {self.files.items()}
        '''

class FileSystem:
    def __init__(self):
        self.root = Directory("root")

    def _parse_path(self, path):
        return path.split("/")
        
    def create(self, path, content):
        path_components = self._parse_path(path)
        directories, file_name = path_components[:len(path_components)-1], path_components[-1]
        i = 0
        curr = self.root
        while i < len(directories):
            new_d = directories[i]
            if new_d not in curr.subdirectories:
                curr.subdirectories[new_d] = Directory(new_d)
            curr = curr.subdirectories[new_d]
            i += 1
        if file_name in curr.files: 
            raise ValueError(f"Cannot add file {file_name} because there is an existing file with the same name")
            # Can potentially append number and save
        curr.files[file_name] = File(file_name, content)


    def _find_file(self, path):
        path_components = self._parse_path(path)
        directories, file_name = path_components[:len(path_components)-1], path_components[-1]
        i = 0
        curr = self.root
        while i < len(directories):
            d = directories[i]
            if d not in curr.subdirectories:
                raise ValueError(f"Directory {d} in path {path} not found")
            curr = curr.subdirectories[d]
            i += 1
        
        if file_name not in curr.files: 
            raise ValueError(f"No file {file_name} exists at path {path}")
        return curr, curr.files[file_name]
        
    def read(self, path):        
        return self._find_file(path)[1].content
        
    def delete(self, path):
        parts = self._find_file(path)
        dir, file = parts[0], parts[1]
        del dir.files[file.name]
        
if __name__ == "__main__":
    fs = FileSystem()
    path1 = "Desktop/practice/netflix.py"
    print(fs._parse_path(path1))
    
    fs.create(path1, "content-anu")
    print(fs.root.subdirectories["Desktop"])
    assert("Desktop" in fs.root.subdirectories)
    
    print(fs._find_file(path1)[1].name)
    fs.delete(path1)
    
    fs._find_file(path1)