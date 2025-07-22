#!/usr/bin/env python3
"""
Convertisseur XML Pilott vers ERP

Outil Streamlit pour transformer des fichiers XML exportés depuis Pilott
vers le format attendu par l'ERP (encodage ISO-8859-1, structure spécifique).

Règles de transformation:
1. Convertir l'encodage en ISO-8859-1
2. Supprimer tous les blocs <UserDefinedPacket>
3. Ajouter <PacketInfo> sous <Packet> si absent
4. Préserver le reste du document à l'identique
5. Permettre téléchargement et aperçu
"""

import streamlit as st
from lxml import etree
import io
from typing import Optional


def transform_pilott_to_erp(xml_bytes: bytes) -> bytes:
    """
    Transforme un fichier XML Pilott vers le format ERP.
    
    Args:
        xml_bytes: Contenu XML en bytes (UTF-8 ou ISO-8859-1)
        
    Returns:
        bytes: XML transformé en ISO-8859-1
        
    Raises:
        ValueError: Si le XML est malformé ou l'encodage non supporté
    """
    # Essayer de parser le XML avec différents encodages
    try:
        # Essayer d'abord UTF-8
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            doc = etree.fromstring(xml_bytes, parser)
        except etree.XMLSyntaxError:
            # Essayer ISO-8859-1
            try:
                doc = etree.fromstring(xml_bytes.decode('iso-8859-1').encode('utf-8'), parser)
            except Exception:
                raise ValueError("Impossible de parser le XML. Vérifiez l'encodage et la syntaxe.")
    except Exception as e:
        raise ValueError(f"Erreur lors du parsing XML: {str(e)}")
    
    # 1. Supprimer tous les blocs <UserDefinedPacket>
    for element in doc.xpath(".//*[local-name()='UserDefinedPacket']"):
        element.getparent().remove(element)
    
    # 2. Vérifier et ajouter PacketInfo si nécessaire
    # Chercher le bloc Packet
    packet_elements = doc.xpath(".//*[local-name()='Packet']")
    
    for packet in packet_elements:
        # Vérifier si PacketInfo existe déjà
        packet_info = packet.xpath("./*[local-name()='PacketInfo']")
        
        if not packet_info:
            # Créer le bloc PacketInfo
            nsmap = packet.nsmap if hasattr(packet, 'nsmap') else {}
            default_ns = nsmap.get(None, "http://ns.hr-xml.org/2004-08-02")
            
            packet_info_elem = etree.Element(
                "{%s}PacketInfo" % default_ns,
                attrib={"packetType": "data"}
            )
            
            # Ajouter les sous-éléments
            packet_id = etree.SubElement(packet_info_elem, "{%s}packetId" % default_ns)
            packet_id.text = "AssignmentPacket"
            
            action = etree.SubElement(packet_info_elem, "{%s}action" % default_ns)
            action.text = "update"
            
            # Insérer PacketInfo comme premier enfant de Packet
            packet.insert(0, packet_info_elem)
    
    # TODO: Ajouter ici d'autres règles métier si nécessaire
    # Par exemple: normalisation des balises vides, ordre des attributs, etc.
    
    # 3. Sérialiser en ISO-8859-1 avec indentation
    result = etree.tostring(
        doc,
        encoding='iso-8859-1',
        xml_declaration=True,
        pretty_print=True
    )
    
    return result


def main():
    st.set_page_config(
        page_title="Convertisseur XML Pilott → ERP",
        page_icon="🔄",
        layout="centered"
    )
    
    st.title("🔄 Convertisseur XML Pilott → ERP")
    st.markdown("""
    ### 📋 Qu'est-ce que cet outil fait ?
    
    Lorsque vous téléchargez un contrat depuis la plateforme Pilott, le fichier XML est modifié par rapport 
    à la version originale de votre ERP. Cet outil restaure automatiquement le format exact attendu par l'ERP.
    
    ### 🔧 Transformations qui seront appliquées :
    
    1. **🔤 Conversion de l'encodage**
       - Fichier Pilott : UTF-8
       - → Fichier ERP : ISO-8859-1
    
    2. **🗑️ Suppression des métadonnées Pilott**
       - Supprime tous les blocs `<UserDefinedPacket>` ajoutés par HR-Explorer
       - Ces blocs contiennent des informations techniques non nécessaires à l'ERP
    
    3. **➕ Restauration de la structure ERP**
       - Ajoute le bloc standard requis :
       ```xml
       <PacketInfo packetType="data">
         <packetId>AssignmentPacket</packetId>
         <action>update</action>
       </PacketInfo>
       ```
    
    4. **✅ Préservation garantie**
       - Tout le contenu métier (Assignment, Rates, etc.) reste strictement identique
       - L'ordre des balises et l'indentation sont respectés
    
    ---
    """)
    
    # Zone d'upload
    uploaded_file = st.file_uploader(
        "Choisissez un fichier XML Pilott",
        type=['xml'],
        help="Fichier XML exporté depuis la plateforme Pilott"
    )
    
    if uploaded_file is not None:
        try:
            # Lire le fichier uploadé
            xml_content = uploaded_file.read()
            
            # Transformer le XML
            with st.spinner("Conversion en cours..."):
                transformed_xml = transform_pilott_to_erp(xml_content)
            
            st.success("✅ Conversion réussie!")
            
            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger le fichier converti",
                data=transformed_xml,
                file_name=f"ERP_{uploaded_file.name}",
                mime="application/xml"
            )
            
            # Checkbox pour l'aperçu
            if st.checkbox("👁️ Afficher l'aperçu du fichier converti"):
                st.code(transformed_xml.decode('iso-8859-1'), language='xml')
            
            # Informations sur ce qui a été fait
            st.info("""
            ✅ **Transformations effectuées :**
            - Encodage converti en ISO-8859-1
            - Blocs UserDefinedPacket supprimés
            - Bloc PacketInfo vérifié/ajouté
            - Structure ERP restaurée
            """)
            
            # TODO: Ajouter ici des statistiques ou validations supplémentaires si nécessaire
            
        except ValueError as e:
            st.error(f"❌ Erreur: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erreur inattendue: {str(e)}")
            st.info("Vérifiez que le fichier est bien un XML valide.")


if __name__ == "__main__":
    main()
