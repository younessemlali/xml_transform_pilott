# Convertisseur XML Pilott → ERP

## Description

Cet outil permet de convertir des fichiers XML de contrats d'intérim exportés depuis la plateforme Pilott vers le format attendu par votre ERP. Il restaure les fichiers dans leur état d'origine en appliquant plusieurs transformations nécessaires.

## Problématique

Lorsqu'un contrat HR-XML est importé puis téléchargé depuis Pilott, plusieurs modifications indésirables sont apportées :
- L'encodage passe de ISO-8859-1 à UTF-8
- Un bloc `<UserDefinedPacket>` avec des métadonnées est ajouté
- Le bloc `<PacketInfo packetType="data">` est supprimé
- Les balises vides sont parfois transformées en balises auto-fermantes

## Solution

L'application effectue automatiquement les transformations suivantes :
1. **Conversion de l'encodage** : UTF-8 → ISO-8859-1
2. **Suppression** de tous les blocs `<UserDefinedPacket>`
3. **Ajout** du bloc `<PacketInfo>` s'il est absent
4. **Préservation** du contenu métier (Assignment, Rates, etc.)
5. **Formatage** identique au modèle ERP

## Installation

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Cloner ou télécharger ce projet

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application

```bash
streamlit run streamlit_xml_converter.py
```

L'application s'ouvrira dans votre navigateur par défaut.

### Processus de conversion

1. **Upload** : Cliquez sur "Browse files" et sélectionnez votre fichier XML exporté de Pilott
2. **Conversion** : La transformation est automatique et instantanée
3. **Téléchargement** : Cliquez sur "📥 Télécharger le fichier converti"
4. **Aperçu** (optionnel) : Cochez "👁️ Afficher l'aperçu" pour vérifier le résultat

### Exemple de structure attendue

**Avant conversion (Pilott)** :
```xml
<?xml version="1.0" encoding="utf-8"?>
<Envelope xmlns="http://ns.hr-xml.org/2004-08-02">
    <UserDefinedPacket>
        <!-- Métadonnées HRExplorer -->
    </UserDefinedPacket>
    <Packet>
        <!-- Pas de PacketInfo -->
        <AssignmentPacket>
            <!-- Contenu métier -->
        </AssignmentPacket>
    </Packet>
</Envelope>
```

**Après conversion (ERP)** :
```xml
<?xml version="1.0" encoding="iso-8859-1"?>
<Envelope xmlns="http://ns.hr-xml.org/2004-08-02">
    <Packet>
        <PacketInfo packetType="data">
            <packetId>AssignmentPacket</packetId>
            <action>update</action>
        </PacketInfo>
        <AssignmentPacket>
            <!-- Contenu métier préservé -->
        </AssignmentPacket>
    </Packet>
</Envelope>
```

## Tests

Pour exécuter les tests unitaires :

```bash
pytest test_transform.py
```

Les tests vérifient :
- La suppression des blocs UserDefinedPacket
- L'ajout correct du bloc PacketInfo
- La gestion des erreurs (XML invalide)
- La conversion d'encodage

## Gestion des erreurs

L'application gère plusieurs types d'erreurs :
- **XML malformé** : Message d'erreur clair avec indication du problème
- **Encodage non supporté** : Tentative automatique avec ISO-8859-1 et UTF-8
- **Fichier non XML** : Rejet avec message explicite

## Architecture technique

- **Interface** : Streamlit pour une UI web simple et efficace
- **Parsing XML** : lxml pour une manipulation robuste du XML
- **Fonction pure** : `transform_pilott_to_erp()` sans effets de bord
- **Tests** : pytest pour la validation

## Support

En cas de problème :
1. Vérifiez que votre fichier est bien un XML valide
2. Assurez-vous qu'il provient bien de Pilott
3. Consultez les messages d'erreur affichés
4. Vérifiez l'encodage du fichier source

## Évolutions futures

Des marqueurs TODO sont présents dans le code pour faciliter l'ajout de règles métier supplémentaires si nécessaire.
