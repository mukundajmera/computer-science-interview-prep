from text_editor import TextEditor

def main():
    editor = TextEditor()
    
    print("Inserting lines...")
    editor.insert(1, "Hello")
    editor.insert(2, "World")
    editor.insert(3, "!")
    editor.display()
    
    print("\nUndoing...")
    editor.undo()
    editor.display()
    
    print("\nRedoing...")
    editor.redo()
    editor.display()
    
    print("\nCopying and pasting...")
    editor.copy(1, 2)
    editor.paste(4)
    editor.display()
    
    print("\nDeleting a range...")
    editor.delete_range(2, 4)
    editor.display()

if __name__ == "__main__":
    main()
