import os

def unite_project_files(output_file="proyecto_completo.txt", ignore_dirs=None):
    if ignore_dirs is None:
        # Carpetas que usualmente no quieres en el documento
        ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.vscode', 'dist', 'build'}
    
    project_root = os.getcwd()
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(project_root):
            # Filtrar carpetas ignoradas
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                # Evitar que el script se lea a sí mismo o al archivo de salida
                if file == output_file or file == os.path.basename(__file__):
                    continue
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_root)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        
                        # Encabezado visual para separar archivos
                        outfile.write(f"\n{'='*80}\n")
                        outfile.write(f"ARCHIVO: {relative_path}\n")
                        outfile.write(f"{'='*80}\n\n")
                        
                        outfile.write(content)
                        outfile.write("\n\n")
                        
                except (UnicodeDecodeError, PermissionError):
                    # Ignorar archivos binarios (imágenes, ejecutables, etc.)
                    continue

    print(f"Proyecto unido con éxito en: {output_file}")

if __name__ == "__main__":
    unite_project_files()