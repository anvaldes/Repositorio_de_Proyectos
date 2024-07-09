import os
import argparse

#----------------------------------------------------------------------

parser = argparse.ArgumentParser(
    description="Clean up directory and put files into according folders."
)

parser.add_argument(
    "--path",
    type=str,
    default=".",
    help="Directory path of the to be cleaned directory",
)

# parse the arguments given by the user and extract the path
args = parser.parse_args()
path = args.path

print(f"Cleaning up directory {path}")

#----------------------------------------------------------------------

dir_content = os.listdir(path)

# create a relative path from the path to the file and the document name
path_dir_content = [os.path.join(path, doc) for doc in dir_content]

docs = [doc for doc in path_dir_content if os.path.isfile(doc)]
folders = [folder for folder in path_dir_content if os.path.isdir(folder)]

created_folders = []

for doc in docs:
    # separate name from file extension
    full_doc_path, filetype = os.path.splitext(doc)
    doc_path = os.path.dirname(full_doc_path)
    doc_name = os.path.basename(full_doc_path)
    
    if filetype == '':

        pass

    else:

        subfolder_path = os.path.join(path, filetype[1:].lower())

        if subfolder_path not in folders and subfolder_path not in created_folders:
            
            try:
                
                os.mkdir(subfolder_path)
                created_folders.append(subfolder_path)
                print(f"Folder {subfolder_path} created.")
                
            except FileExistsError as err:
                
                print(f"Folder already exists at {subfolder_path}... {err}")
        
        new_doc_path = os.path.join(subfolder_path, doc_name) + filetype
        os.rename(doc, new_doc_path)

        print(f"Moved file {doc} to {new_doc_path}")

#----------------------------------------------------------------------

