import struct
from typing import Dict, List, Optional, Tuple
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.exceptions import InvalidSignature

class CertAnalyzer:
    def __init__(self):
        self.certificates = []
        self.private_keys = []
        self.public_keys = []
        
    def analyze_certificate(self, cert_data: bytes) -> Dict:
        """Analyze a certificate and extract its information"""
        try:
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Extract information from the certificate
            subject = dict(cert.subject)
            issuer = dict(cert.issuer)
            valid_from = cert.not_valid_before
            valid_until = cert.not_valid_after
            serial_number = cert.serial_number
            public_key = cert.public_key()
            
            cert_info = {
                'subject': subject,
                'issuer': issuer,
                'valid_from': valid_from,
                'valid_until': valid_until,
                'serial_number': serial_number,
                'public_key': {
                    'type': type(public_key).__name__,
                    'size': public_key.key_size if hasattr(public_key, 'key_size') else None
                }
            }
            
            self.certificates.append(cert_info)
            return cert_info
            
        except Exception as e:
            return {'error': str(e)}
            
    def analyze_private_key(self, key_data: bytes) -> Dict:
        """Analyze a private key and extract its information"""
        try:
            key = load_pem_private_key(key_data, password=None)
            
            key_info = {
                'type': type(key).__name__,
                'size': key.key_size if hasattr(key, 'key_size') else None
            }
            
            self.private_keys.append(key_info)
            return key_info
            
        except Exception as e:
            return {'error': str(e)}
            
    def analyze_public_key(self, key_data: bytes) -> Dict:
        """Analyze a public key and extract its information"""
        try:
            key = load_pem_public_key(key_data)
            
            key_info = {
                'type': type(key).__name__,
                'size': key.key_size if hasattr(key, 'key_size') else None
            }
            
            self.public_keys.append(key_info)
            return key_info
            
        except Exception as e:
            return {'error': str(e)}
            
    def verify_signature(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify a digital signature"""
        try:
            key = load_pem_public_key(public_key)
            
            if isinstance(key, rsa.RSAPublicKey):
                key.verify(
                    signature,
                    data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
            elif isinstance(key, ec.EllipticCurvePublicKey):
                key.verify(
                    signature,
                    data,
                    ec.ECDSA(hashes.SHA256())
                )
            else:
                return False
                
            return True
            
        except InvalidSignature:
            return False
        except Exception:
            return False
            
    def get_certificate_chain(self, cert_data: bytes) -> List[Dict]:
        """Build the certificate chain"""
        try:
            cert = x509.load_pem_x509_certificate(cert_data)
            chain = []
            
            while cert:
                chain.append({
                    'subject': dict(cert.subject),
                    'issuer': dict(cert.issuer),
                    'serial_number': cert.serial_number
                })
                
                # Search for the issuer certificate
                issuer_cert = None
                for stored_cert in self.certificates:
                    if stored_cert['subject'] == dict(cert.issuer):
                        issuer_cert = stored_cert
                        break
                        
                if not issuer_cert:
                    break
                    
                cert = x509.load_pem_x509_certificate(issuer_cert['data'])
                
            return chain
            
        except Exception as e:
            return [{'error': str(e)}] 