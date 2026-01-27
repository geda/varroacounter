import os
import glob

# Chemin vers les fichiers de labels
labels_path = "Varroa-counter-2/test/labels/*.txt"

# Récupérer tous les fichiers .txt
label_files = glob.glob(labels_path)

print(f"Nombre de fichiers trouvés: {len(label_files)}")

# Traiter chaque fichier
for filepath in label_files:
    # Lire le contenu du fichier
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Modifier chaque ligne
    new_lines = []
    for line in lines:
        # Séparer la ligne en parties
        parts = line.strip().split()
        if len(parts) > 0:
            # Remplacer le premier nombre par 0
            parts[0] = '0'
            # Reconstruire la ligne
            new_lines.append(' '.join(parts) + '\n')
        else:
            new_lines.append(line)

    # Écrire le contenu modifié
    with open(filepath, 'w') as f:
        f.writelines(new_lines)

    print(f"Modifié: {os.path.basename(filepath)}")

print("Terminé!")