import pytest
from streamlit_xml_converter import transform_pilott_to_erp

def test_transform_removes_userdefined_packet():
    """Test que UserDefinedPacket est bien supprimé et PacketInfo ajouté"""
    input_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<Envelope xmlns="http://ns.hr-xml.org/2004-08-02">
    <UserDefinedPacket>
        <test>data</test>
    </UserDefinedPacket>
    <Packet>
        <AssignmentPacket/>
    </Packet>
</Envelope>"""
    
    result = transform_pilott_to_erp(input_xml)
    assert b'UserDefinedPacket' not in result
    assert b'PacketInfo' in result
    assert b'encoding="iso-8859-1"' in result

def test_transform_preserves_existing_packet_info():
    """Test que PacketInfo existant n'est pas dupliqué"""
    input_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<Envelope xmlns="http://ns.hr-xml.org/2004-08-02">
    <Packet>
        <PacketInfo packetType="data">
            <packetId>AssignmentPacket</packetId>
            <action>update</action>
        </PacketInfo>
        <AssignmentPacket/>
    </Packet>
</Envelope>"""
    
    result = transform_pilott_to_erp(input_xml)
    # Compter les occurrences de PacketInfo
    assert result.count(b'PacketInfo') == 2  # Une ouverture, une fermeture

def test_transform_invalid_xml():
    """Test qu'une erreur est levée pour un XML invalide"""
    with pytest.raises(ValueError):
        transform_pilott_to_erp(b"Not valid XML")

def test_transform_iso_8859_1_input():
    """Test avec un fichier déjà en ISO-8859-1"""
    input_xml = """<?xml version="1.0" encoding="iso-8859-1"?>
<Envelope xmlns="http://ns.hr-xml.org/2004-08-02">
    <Packet>
        <AssignmentPacket>
            <Name>Employé</Name>
        </AssignmentPacket>
    </Packet>
</Envelope>""".encode('iso-8859-1')
    
    result = transform_pilott_to_erp(input_xml)
    assert b'encoding="iso-8859-1"' in result
    assert b'PacketInfo' in result
