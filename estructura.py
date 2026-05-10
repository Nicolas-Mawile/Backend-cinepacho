import os

def generate_tree(startpath, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.vscode', '.idea'}

    output = []
    output.append(f"Estructura de: {os.path.basename(os.getcwd())}/")
    
    for root, dirs, files in os.walk(startpath):
        # Filtrar carpetas ignoradas
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root)
        
        if folder_name:
            output.append(f"{indent}├── {folder_name}/")
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            output.append(f"{sub_indent}└── {f}")
            
    return "\n".join(output)

if __name__ == "__main__":
    ruta_proyecto = os.getcwd()
    resultado = generate_tree(ruta_proyecto)
    
    # Guardar en un archivo
    with open("estructura_proyecto.txt", "w", encoding="utf-8") as f:
        f.write(resultado)
    
    # Mostrar en consola
    print(resultado)
    print("\n[!] Estructura guardada en 'estructura_proyecto.txt'")