import os

def generate_tree(startpath, exclude_dirs):
    output = []
    for root, dirs, files in os.walk(startpath):
        # Filtrar carpetas excluidas
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        output.append(f'{indent}{os.path.basename(root)}/')
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.startswith('.'):  # Omitir archivos ocultos
                output.append(f'{sub_indent}{f}')
    
    return '\n'.join(output)

if __name__ == "__main__":
    # Define aquí las carpetas que quieres ignorar
    folders_to_ignore = [
        'venv', '__pycache__', 'node_modules', 
        'target', '.git', '.idea', '.vscode'
    ]
    
    current_dir = os.getcwd()
    tree_structure = generate_tree(current_dir, folders_to_ignore)
    
    with open("proyecto_estructura.txt", "w", encoding="utf-8") as f:
        f.write(tree_structure)
        
    print("✅ Estructura generada en 'proyecto_estructura.txt'")